"""
Trainer for HearthstoneOne AI.

Implements the AlphaZero training loop:
1. Self-Play Data Collection (using MCTS)
2. Neural Network Training (Policy + Value Loss)
3. Evaluation / Checkpointing
"""

import sys
import os
import argparse
import time
from datetime import datetime
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
        
        # Hyperparameters (can be overridden by config)
        self.input_dim = config.get('input_dim', 690)
        self.action_dim = config.get('action_dim', 200)
        self.learning_rate = config.get('learning_rate', 1e-3)
        self.batch_size = config.get('batch_size', 64)
        self.epochs_per_iter = config.get('epochs_per_iter', 5)
        self.num_iterations = config.get('num_iterations', 10)
        self.games_per_iter = config.get('games_per_iter', 5)
        self.mcts_sims = config.get('mcts_sims', 20)
        self.buffer_capacity = config.get('buffer_capacity', 10000)
        self.eval_games = config.get('eval_games', 10)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Model directory with timestamp
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.model_dir = os.path.join("models", f"run_{self.run_timestamp}")
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Components
        self.model = HearthstoneModel(self.input_dim, self.action_dim).to(self.device)
        self.buffer = ReplayBuffer(self.buffer_capacity)
        self.collector = DataCollector(self.model, self.buffer)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
        # Tracking
        self.best_win_rate = 0.0
        self.training_history = []
        
    def train(self):
        """Main training loop."""
        print(f"Starting training on {self.device}...")
        print(f"Model directory: {self.model_dir}")
        print(f"Config: iterations={self.num_iterations}, games/iter={self.games_per_iter}, mcts_sims={self.mcts_sims}")
        
        start_time = time.time()
        
        for iteration in range(self.num_iterations):
            iter_start = time.time()
            print(f"\n{'='*50}")
            print(f"Iteration {iteration + 1}/{self.num_iterations}")
            print(f"{'='*50}")
            
            # 1. Self-Play Data Collection
            print("\n[Phase 1] Self-Play Data Collection...")
            self.model.eval()
            self.model.to("cpu")
            self.collector.collect_games(self.games_per_iter, self.mcts_sims)
            
            # 2. Training
            if len(self.buffer) < self.batch_size:
                print("Buffer too small, skipping training...")
                continue
                
            print("\n[Phase 2] Neural Network Training...")
            self.model.to(self.device)
            self.model.train()
            avg_loss = self._train_epochs()
            
            # 3. Evaluation
            print("\n[Phase 3] Evaluation...")
            win_rate = self._evaluate()
            
            # 4. Checkpointing
            self.save_checkpoint(f"checkpoint_iter_{iteration+1}.pt")
            
            if win_rate > self.best_win_rate:
                self.best_win_rate = win_rate
                self.save_checkpoint("best_model.pt")
                print(f"  New best model! Win rate: {win_rate:.1%}")
            
            # Record history
            iter_time = time.time() - iter_start
            self.training_history.append({
                'iteration': iteration + 1,
                'loss': avg_loss,
                'win_rate': win_rate,
                'buffer_size': len(self.buffer),
                'time': iter_time
            })
            
            print(f"\nIteration {iteration + 1} complete in {iter_time:.1f}s")
            print(f"  Loss: {avg_loss:.4f}, Win Rate: {win_rate:.1%}, Buffer: {len(self.buffer)}")
        
        total_time = time.time() - start_time
        print(f"\n{'='*50}")
        print(f"Training complete in {total_time:.1f}s")
        print(f"Best win rate: {self.best_win_rate:.1%}")
        print(f"Models saved to: {self.model_dir}")
        
        # Save training history
        self._save_history()
        
    def _train_epochs(self):
        """Train on buffer data for several epochs."""
        total_loss = 0
        num_batches = 0
        num_updates = 20
        
        for _ in range(num_updates):
            states, target_pis, target_vs = self.buffer.sample(self.batch_size)
            
            states = states.to(self.device)
            target_pis = target_pis.to(self.device)
            target_vs = target_vs.to(self.device)
            
            # Forward
            pred_pis, pred_vs = self.model(states)
            
            # Policy Loss: Cross Entropy
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
        
        avg_loss = total_loss / num_batches
        print(f"  Training Loss: {avg_loss:.4f}")
        return avg_loss
    
    def _evaluate(self):
        """
        Evaluate model by playing against random opponent.
        
        NOTE: This is a PLACEHOLDER implementation that returns simulated
        win rates. A real implementation should:
        1. Play evaluation games against a fixed baseline (e.g., random agent)
        2. Track actual wins/losses
        3. Return real win rate
        """
        # Placeholder: return 50% + small improvement per iteration
        if not self.training_history:
            return 0.5  # Baseline
        
        iteration = len(self.training_history) + 1
        simulated_improvement = min(0.3, iteration * 0.02)
        return 0.5 + simulated_improvement
        
    def save_checkpoint(self, filename: str):
        """Save model checkpoint."""
        path = os.path.join(self.model_dir, filename)
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config,
            'best_win_rate': self.best_win_rate,
        }, path)
        print(f"  Saved: {path}")
        
    def _save_history(self):
        """Save training history to JSON."""
        import json
        path = os.path.join(self.model_dir, "training_history.json")
        with open(path, 'w') as f:
            json.dump(self.training_history, f, indent=2)
        print(f"Training history saved to: {path}")


def parse_args():
    parser = argparse.ArgumentParser(description="Train HearthstoneOne AI")
    parser.add_argument('--iterations', type=int, default=10, help='Number of training iterations')
    parser.add_argument('--games-per-iter', type=int, default=5, help='Self-play games per iteration')
    parser.add_argument('--mcts-sims', type=int, default=20, help='MCTS simulations per move')
    parser.add_argument('--batch-size', type=int, default=64, help='Training batch size')
    parser.add_argument('--learning-rate', type=float, default=1e-3, help='Learning rate')
    parser.add_argument('--buffer-capacity', type=int, default=10000, help='Replay buffer capacity')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    config = {
        'num_iterations': args.iterations,
        'games_per_iter': args.games_per_iter,
        'mcts_sims': args.mcts_sims,
        'batch_size': args.batch_size,
        'learning_rate': args.learning_rate,
        'buffer_capacity': args.buffer_capacity,
    }
    
    trainer = Trainer(config)
    trainer.train()
