"""
Imitation Learning Trainer for HearthstoneOne AI.

Trains the Transformer model using behavior cloning on human replay data.
"""

import os
import sys

# Fix for PyTorch MPS nested tensor error
# https://github.com/pytorch/pytorch/issues/112836
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import List, Tuple, Optional
import time
import json

# Fix for PyTorch MPS nested tensor error
# https://github.com/pytorch/pytorch/issues/112836
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.transformer_model import CardTransformer, SequenceEncoder
from ai.device import get_best_device


class ReplayDataset(Dataset):
    """
    PyTorch Dataset for replay training data.
    
    Expects preprocessed data with:
    - card_ids: [seq_len] card ID indices
    - card_features: [seq_len, 11] card features
    - action_label: Action index (for policy supervision)
    - game_outcome: 1 for win, -1 for loss, 0 for unknown
    """
    
    def __init__(self, data_path: str = None, data: List[dict] = None):
        if data_path and os.path.exists(data_path):
            with open(data_path, 'r') as f:
                content = json.load(f)
                if isinstance(content, dict) and 'samples' in content:
                    self.samples = content['samples']
                else:
                    self.samples = content
        elif data:
            self.samples = data
        else:
            self.samples = []
        
        self.encoder = SequenceEncoder()
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, int, float]:
        sample = self.samples[idx]
        
        # Get tensors (already preprocessed or encode on-the-fly)
        if 'card_ids' in sample:
            card_ids = torch.tensor(sample['card_ids'], dtype=torch.long)
            card_features = torch.tensor(sample['card_features'], dtype=torch.float32)
            attention_mask = (card_ids != 0)
        else:
            # Minimal sample - create dummy tensors
            seq_len = 24  # MAX_SEQUENCE_LENGTH
            card_ids = torch.zeros(seq_len, dtype=torch.long)
            card_features = torch.zeros(seq_len, 11, dtype=torch.float32)
            attention_mask = torch.zeros(seq_len, dtype=torch.bool)
        
        action_label = sample.get('action_label', 0)
        game_outcome = sample.get('game_outcome', 0.0)
        
        return card_ids, card_features, attention_mask, action_label, game_outcome


class ImitationTrainer:
    """
    Trains CardTransformer using behavior cloning.
    
    Loss = CrossEntropy(policy, human_action) + MSE(value, game_outcome)
    """
    
    def __init__(self,
                 model: CardTransformer = None,
                 learning_rate: float = 1e-4,
                 batch_size: int = 32,
                 device: str = None):
        
        self.device = device or get_best_device()
        
        self.model = model or CardTransformer()
        self.model.to(self.device)
        
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=100, eta_min=1e-6
        )
        
        self.batch_size = batch_size
        self.train_history = []
    
    def train_epoch(self, dataloader: DataLoader) -> float:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        for batch in dataloader:
            card_ids, card_features, attention_mask, action_labels, outcomes = batch
            
            # Move to device
            card_ids = card_ids.to(self.device)
            card_features = card_features.to(torch.float32).to(self.device)
            attention_mask = attention_mask.to(self.device)
            action_labels = action_labels.to(self.device)
            outcomes = outcomes.to(torch.float32).to(self.device).unsqueeze(1)
            
            # Forward pass
            policy, value = self.model(card_ids, card_features, attention_mask)
            
            # Policy loss (NLL for log-probabilities)
            log_policy = torch.log(policy + 1e-8)
            policy_loss = F.nll_loss(log_policy, action_labels)
            
            # Value loss (MSE with game outcome)
            value_loss = F.mse_loss(value, outcomes)
            
            # Combined loss
            loss = policy_loss + 0.5 * value_loss
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
        
        self.scheduler.step()
        
        return total_loss / max(num_batches, 1)
    
    def evaluate(self, dataloader: DataLoader) -> Tuple[float, float]:
        """Evaluate model on validation set."""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch in dataloader:
                card_ids, card_features, attention_mask, action_labels, outcomes = batch
                
                card_ids = card_ids.to(self.device)
                card_features = card_features.to(torch.float32).to(self.device)
                attention_mask = attention_mask.to(self.device)
                action_labels = action_labels.to(self.device)
                outcomes = outcomes.to(torch.float32).to(self.device).unsqueeze(1)
                
                policy, value = self.model(card_ids, card_features, attention_mask)
                
                # Accuracy
                predictions = policy.argmax(dim=1)
                correct += (predictions == action_labels).sum().item()
                total += action_labels.size(0)
                
                # Loss
                log_policy = torch.log(policy + 1e-8)
                policy_loss = F.nll_loss(log_policy, action_labels)
                value_loss = F.mse_loss(value, outcomes)
                total_loss += (policy_loss + 0.5 * value_loss).item()
        
        accuracy = correct / max(total, 1)
        avg_loss = total_loss / max(len(dataloader), 1)
        
        return avg_loss, accuracy
    
    def train(self,
              train_data: List[dict],
              val_data: List[dict] = None,
              num_epochs: int = 50,
              save_path: str = "models/transformer_model.pt"):
        """
        Full training loop.
        
        Args:
            train_data: List of training samples
            val_data: Optional validation samples
            num_epochs: Number of training epochs
            save_path: Path to save best model
        """
        train_dataset = ReplayDataset(data=train_data)
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        
        val_loader = None
        if val_data:
            val_dataset = ReplayDataset(data=val_data)
            val_loader = DataLoader(val_dataset, batch_size=self.batch_size)
        
        best_val_loss = float('inf')
        
        print(f"Training on {len(train_data)} samples for {num_epochs} epochs")
        print(f"Device: {self.device}")
        print("=" * 50)
        
        for epoch in range(num_epochs):
            start_time = time.time()
            
            # Train
            train_loss = self.train_epoch(train_loader)
            
            # Validate
            val_loss, val_acc = 0.0, 0.0
            if val_loader:
                val_loss, val_acc = self.evaluate(val_loader)
            
            epoch_time = time.time() - start_time
            
            print(f"Epoch {epoch + 1}/{num_epochs} ({epoch_time:.1f}s)")
            print(f"  Train Loss: {train_loss:.4f}")
            if val_loader:
                print(f"  Val Loss: {val_loss:.4f}, Accuracy: {val_acc:.2%}")
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self.save(save_path)
                print(f"  -> Saved best model")
            
            self.train_history.append({
                'epoch': epoch + 1,
                'train_loss': train_loss,
                'val_loss': val_loss,
                'val_accuracy': val_acc
            })
        
        print("\n" + "=" * 50)
        print(f"Training complete. Best val loss: {best_val_loss:.4f}")
    
    def save(self, path: str):
        """Save model checkpoint."""
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'train_history': self.train_history
        }, path)
    
    def load(self, path: str):
        """Load model checkpoint."""
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.train_history = checkpoint.get('train_history', [])


def create_dummy_training_data(num_samples: int = 1000) -> List[dict]:
    """Create dummy data for testing the training pipeline."""
    samples = []
    seq_len = 24
    
    for _ in range(num_samples):
        sample = {
            'card_ids': [0] * seq_len,  # All padding
            'card_features': [[0.0] * 11 for _ in range(seq_len)],
            'action_label': np.random.randint(0, 200),
            'game_outcome': np.random.choice([-1.0, 1.0])
        }
        samples.append(sample)
    
    return samples


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Transformer with Imitation Learning')
    parser.add_argument('--data', type=str, help='Path to training data JSON')
    parser.add_argument('--epochs', type=int, default=50, help='Training epochs')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
    parser.add_argument('--lr', type=float, default=1e-4, help='Learning rate')
    parser.add_argument('--output', type=str, default='models/transformer_model.pt',
                        help='Output model path')
    parser.add_argument('--dummy', action='store_true', help='Use dummy data for testing')
    
    args = parser.parse_args()
    
    # Create or load data
    if args.dummy:
        print("Using dummy data for testing...")
        train_data = create_dummy_training_data(1000)
        val_data = create_dummy_training_data(200)
    elif args.data:
        with open(args.data, 'r') as f:
            content = json.load(f)
        
        if isinstance(content, dict) and 'samples' in content:
            data = content['samples']
            print(f"Loaded {len(data)} samples from {args.data} (Games played: {content.get('games_played', '?')})")
        else:
            data = content
            print(f"Loaded {len(data)} samples from {args.data}")
            
        split = int(len(data) * 0.9)
        train_data = data[:split]
        val_data = data[split:]
    else:
        print("No data provided. Use --data or --dummy")
        exit(1)
    
    # Train
    model = CardTransformer()
    trainer = ImitationTrainer(model, learning_rate=args.lr, batch_size=args.batch_size)
    trainer.train(train_data, val_data, num_epochs=args.epochs, save_path=args.output)
