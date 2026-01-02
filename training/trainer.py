"""
Trainer for HearthstoneOne AI.

Implements the AlphaZero training loop:
1. Self-Play Data Collection (using MCTS)
2. Neural Network Training (Policy + Value Loss)
3. Evaluation / Checkpointing
"""

import sys
import os
import torch
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

# Path hacks
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.model import HearthstoneModel
from ai.replay_buffer import ReplayBuffer
from training.data_collector import DataCollector

class Trainer:
    def __init__(self, config=None):
        self.config = config or {}
        
        # Hyperparameters
        self.input_dim = 690
        self.action_dim = 200
        self.learning_rate = 1e-3
        self.batch_size = 64
        self.epochs_per_iter = 5
        self.num_iterations = 10
        self.games_per_iter = 5
        self.mcts_sims = 20
        self.buffer_capacity = 10000
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Components
        self.model = HearthstoneModel(self.input_dim, self.action_dim).to(self.device)
        self.buffer = ReplayBuffer(self.buffer_capacity)
        self.collector = DataCollector(self.model, self.buffer)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
    def train(self):
        """Main training loop."""
        print(f"Starting training on {self.device}...")
        
        for iteration in range(self.num_iterations):
            print(f"\n=== Iteration {iteration + 1}/{self.num_iterations} ===")
            
            # 1. Self-Play
            self.model.eval() # Collect in eval mode
            # Note: DataCollector uses model on CPU usually for MCTS simplicity unless moved.
            # My current MCTS code calls model(tensor), so model needs to be wherever tensor is.
            # DataCollector uses MCTS.
            # MCTS `_expand` calls `self.model(tensor)`.
            # We should keep collecting on CPU for ease or handle device carefully.
            # For simplicity, move model to CPU for collection, GPU for training.
            self.model.to("cpu")
            self.collector.collect_games(self.games_per_iter, self.mcts_sims)
            
            # 2. Training
            if len(self.buffer) < self.batch_size:
                print("Buffer too small, skipping train...")
                continue
                
            self.model.to(self.device)
            self.model.train()
            self._train_epochs()
            
            # 3. Checkpoint
            self.save_checkpoint(f"checkpoint_iter_{iteration+1}.pt")
            
    def _train_epochs(self):
        """Train on buffer data for several epochs."""
        # Sample directly from buffer to create a dataset? 
        # Or just sample batches manually?
        # ReplayBuffer.sample returns a batch.
        
        total_loss = 0
        num_batches = 0
        
        # Train for fixed number of updates or cover buffer?
        # Usually train on sample of buffer.
        
        # Let's do 100 updates per iteration
        num_updates = 20
        
        for _ in range(num_updates):
            states, target_pis, target_vs = self.buffer.sample(self.batch_size)
            
            states = states.to(self.device)
            target_pis = target_pis.to(self.device)
            target_vs = target_vs.to(self.device)
            
            # Forward
            pred_pis, pred_vs = self.model(states)
            
            # Loss
            # Policy Loss: Cross Entropy between target_pi (probs) and pred_pi (logits or probs?)
            # Model output depends on Implementation.
            # Step 1564 ai/model.py:
            # return F.softmax(policy, dim=-1), torch.tanh(value)
            # So output is PROBS.
            # We calculate loss: - sum(target * log(pred))
            
            # Clamp for stability
            pred_pis = torch.clamp(pred_pis, 1e-8, 1.0)
            policy_loss = -torch.sum(target_pis * torch.log(pred_pis)) / target_pis.size(0)
            
            # Value Loss: MSE
            value_loss = F.mse_loss(pred_vs, target_vs)
            
            loss = policy_loss + value_loss
            
            # Backward
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
            
        print(f"Training Loss: {total_loss / num_batches:.4f}")
        
    def save_checkpoint(self, filename: str):
        """Save model."""
        path = os.path.join("models", filename)
        os.makedirs("models", exist_ok=True)
        torch.save(self.model.state_dict(), path)
        print(f"Saved model to {path}")

if __name__ == "__main__":
    trainer = Trainer()
    trainer.train()
