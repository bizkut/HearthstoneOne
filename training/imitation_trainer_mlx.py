"""
Imitation Learning Trainer for HearthstoneOne AI (MLX Version).

Trains the Transformer model using behavior cloning on human replay data.
Optimized for Apple Silicon.
"""

import os
import sys
import json
import time
import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import mlx.utils
from typing import List, Tuple, Optional, Generator

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.mlx_transformer_model import CardTransformer, MAX_BOARD_SIZE, MAX_HAND_SIZE

def batch_iterate(batch_size: int, *args) -> Generator:
    """Yield batches of data."""
    if len(args) == 0:
        return
    
    start = 0
    n = len(args[0])
    
    # Shuffle indices
    perm = np.random.permutation(n)
    
    while start < n:
        end = min(start + batch_size, n)
        ids = perm[start:end]
        
        yield tuple(arg[ids] for arg in args)
        start += batch_size

class ReplayDataset:
    """
    Dataset handler for replay training data.
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
            
        print(f"Processing {len(self.samples)} samples...")
        
        # Pre-process into numpy arrays to avoid overhead during training
        # This mirrors the GPU caching strategy but using system RAM which is unified on Apple Silicon results in zero-copy access usually
        self.card_ids, self.card_features, self.masks, self.action_labels, self.outcomes = self._process_samples()
        
    def _process_samples(self):
        seq_len = 24
        num_samples = len(self.samples)
        
        card_ids = np.zeros((num_samples, seq_len), dtype=np.int32)
        card_features = np.zeros((num_samples, seq_len, 11), dtype=np.float32)
        masks = np.zeros((num_samples, seq_len), dtype=bool) # True = valid
        action_labels = np.zeros((num_samples,), dtype=np.int32)
        outcomes = np.zeros((num_samples, 1), dtype=np.float32)
        
        for i, sample in enumerate(self.samples):
            if 'card_ids' in sample:
                c_ids = sample['card_ids']
                # Pad or truncate
                curr_len = len(c_ids)
                if curr_len > seq_len:
                    c_ids = c_ids[:seq_len]
                    c_feats = sample['card_features'][:seq_len]
                else:
                    c_feats = sample['card_features']
                
                # Assign
                l = min(curr_len, seq_len)
                card_ids[i, :l] = c_ids[:l]
                card_features[i, :l] = c_feats[:l]
                masks[i, :l] = (np.array(c_ids[:l]) != 0)
                
            action_labels[i] = sample.get('action_label', 0)
            outcomes[i, 0] = sample.get('game_outcome', 0.0)
            
        return card_ids, card_features, masks, action_labels, outcomes
    
    def __len__(self):
        return len(self.samples)

def loss_fn(model, card_ids, card_features, mask, action_labels, outcomes):
    policy, value = model(card_ids, card_features, mask)
    
    # Policy loss (Cross Entropy)
    # MLX Cross Entropy expects logits and indices
    policy_loss = nn.losses.cross_entropy(policy, action_labels)
    policy_loss = mx.mean(policy_loss)
    
    # Value loss (MSE)
    value_loss = nn.losses.mse_loss(value, outcomes)
    
    return policy_loss + 0.5 * value_loss, (policy, value)

class ImitationTrainer:
    """
    Trains CardTransformer using behavior cloning with MLX.
    """
    
    def __init__(self,
                 model: CardTransformer,
                 learning_rate: float = 1e-4,
                 batch_size: int = 32):
        
        self.model = model
        self.optimizer = optim.AdamW(learning_rate=learning_rate)
        self.batch_size = batch_size
        self.train_history = []
        
        # Compile the training step
        self.state = [self.model.state, self.optimizer.state]
        
        # @mx.compile
        def step(ids, feats, m, labels, out):
            loss_and_grad_fn = nn.value_and_grad(self.model, loss_fn)
            (loss, (policy, value)), grads = loss_and_grad_fn(self.model, ids, feats, m, labels, out)
            self.optimizer.update(self.model, grads)
            return loss, policy, value
        
        self.train_step = step

    def train_epoch(self, dataset: ReplayDataset) -> float:
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        for batch_ids, batch_feats, batch_mask, batch_labels, batch_out in batch_iterate(
            self.batch_size, 
            dataset.card_ids, 
            dataset.card_features, 
            dataset.masks, 
            dataset.action_labels, 
            dataset.outcomes
        ):
            # Convert to MLX arrays
            ids = mx.array(batch_ids)
            feats = mx.array(batch_feats)
            m = mx.array(batch_mask)
            labels = mx.array(batch_labels)
            out = mx.array(batch_out)
            
            # Train step
            loss, _, _ = self.train_step(ids, feats, m, labels, out)
            
            # Force eval to get value
            mx.eval(loss, self.model.parameters()) # Just eval loss and params to ensure update happened
            
            total_loss += loss.item()
            num_batches += 1
            
        return total_loss / max(num_batches, 1)

    def evaluate(self, dataset: ReplayDataset) -> Tuple[float, float]:
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        # No compile for eval loop usually, just direct inference
        for batch_ids, batch_feats, batch_mask, batch_labels, batch_out in batch_iterate(
            self.batch_size, 
            dataset.card_ids, 
            dataset.card_features, 
            dataset.masks, 
            dataset.action_labels, 
            dataset.outcomes
        ):
            ids = mx.array(batch_ids)
            feats = mx.array(batch_feats)
            m = mx.array(batch_mask)
            labels = mx.array(batch_labels)
            out = mx.array(batch_out)
            
            policy, value = self.model(ids, feats, m)
            
            # Loss
            p_loss = nn.losses.cross_entropy(policy, labels)
            v_loss = nn.losses.mse_loss(value, out)
            loss = mx.mean(p_loss) + 0.5 * v_loss
            
            total_loss += loss.item()
            
            # Accuracy
            # argmax along axis 1
            preds = mx.argmax(policy, axis=1)
            correct += mx.sum(preds == labels).item()
            total += labels.shape[0]
            
        return total_loss / max(1, total // self.batch_size), correct / max(total, 1)

    def train(self,
              train_data: List[dict],
              val_data: List[dict] = None,
              num_epochs: int = 50,
              save_path: str = "models/mlx_transformer_model.npz"):
        
        train_dataset = ReplayDataset(data=train_data)
        
        val_dataset = None
        if val_data:
            val_dataset = ReplayDataset(data=val_data)
            
        print(f"Training on {len(train_data)} samples for {num_epochs} epochs")
        print(f"Device: {mx.default_device()}")
        
        # Parameter count
        def count_params(tree):
            if isinstance(tree, mx.array):
                return tree.size
            elif isinstance(tree, dict):
                return sum(count_params(v) for v in tree.values())
            elif isinstance(tree, (list, tuple)):
                return sum(count_params(v) for v in tree)
            return 0
            
        params = count_params(self.model.parameters())
        print(f"Model params: {params:,}")
        print("=" * 50)
        
        best_acc = 0.0
        
        for epoch in range(num_epochs):
            start = time.time()
            
            train_loss = self.train_epoch(train_dataset)
            
            val_loss, val_acc = 0.0, 0.0
            if val_dataset:
                val_loss, val_acc = self.evaluate(val_dataset)
                
            dt = time.time() - start
            
            print(f"Epoch {epoch + 1}/{num_epochs} ({dt:.2f}s) | Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Acc: {val_acc:.2%}")
            
            if val_acc > best_acc:
                best_acc = val_acc
                # Save weights
                self.model.save_weights(save_path)
                print(f"  -> Saved best model")

def create_dummy_training_data(num_samples: int = 1000) -> List[dict]:
    """Create dummy data for testing the training pipeline."""
    samples = []
    seq_len = 24
    
    for _ in range(num_samples):
        sample = {
            'card_ids': [1]*5 + [0] * (seq_len-5),
            'card_features': [[0.1] * 11 for _ in range(seq_len)],
            'action_label': np.random.randint(0, 200),
            'game_outcome': np.random.choice([-1.0, 1.0])
        }
        samples.append(sample)
    
    return samples

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train MLX Transformer')
    parser.add_argument('--data', type=str, help='Path to training data JSON')
    parser.add_argument('--epochs', type=int, default=50, help='Training epochs')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
    parser.add_argument('--lr', type=float, default=1e-4, help='Learning rate')
    parser.add_argument('--output', type=str, default='models/mlx_transformer_model.npz',
                        help='Output model path')
    parser.add_argument('--dummy', action='store_true', help='Use dummy data for testing')
    
    args = parser.parse_args()
    
    if args.dummy:
        print("Using dummy data...")
        train_data = create_dummy_training_data(1000)
        val_data = create_dummy_training_data(200)
    elif args.data:
        with open(args.data, 'r') as f:
            content = json.load(f)
        if isinstance(content, dict) and 'samples' in content:
            data = content['samples']
        else:
            data = content
            
        split = int(len(data) * 0.9)
        train_data = data[:split]
        val_data = data[split:]
    else:
        print("No data. Use --dummy or --data")
        exit(1)
        
    model = CardTransformer()
    trainer = ImitationTrainer(model, learning_rate=args.lr, batch_size=args.batch_size)
    trainer.train(train_data, val_data, num_epochs=args.epochs, save_path=args.output)
