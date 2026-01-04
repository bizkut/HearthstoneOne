#!/usr/bin/env python3
"""
AlphaZero Self-Play Generator for HearthstoneOne.

GPU-Optimized version with:
- Multiprocessing for parallel game simulation
- Batched GPU inference for maximum throughput
"""

import sys
import os
import json
import random
import argparse
import numpy as np
import torch
import torch.multiprocessing as mp
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from queue import Empty
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.game import Game
from simulator.player import Player
from simulator.enums import CardType, Zone
from simulator.card_loader import CardDatabase, create_card

# Reuse existing wrappers
from scripts.generate_self_play import (
    MetaDeckLoader, 
    HERO_BY_CLASS, 
    GameStateWrapper,
    PlayerWrapper,
    CardWrapper
)

from ai.transformer_model import CardTransformer, SequenceEncoder


def get_device():
    """Get the best available device (CUDA > MPS > CPU)."""
    if torch.cuda.is_available():
        return torch.device('cuda')
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return torch.device('mps')
    return torch.device('cpu')


class InferenceServer:
    """
    Handles batched GPU inference for multiple game workers.
    Collects requests, batches them, runs inference, returns results.
    """
    
    def __init__(self, model_path: str, device: torch.device, batch_size: int = 32):
        self.device = device
        self.batch_size = batch_size
        self.encoder = SequenceEncoder()
        
        # Load model
        print(f"Loading model from {model_path}...")
        checkpoint = torch.load(model_path, map_location=device, weights_only=False)
        state_dict = checkpoint.get('model_state_dict', checkpoint)
        
        # Auto-detect architecture
        hidden_dim = state_dict['cls_token'].shape[-1]
        num_layers = max([int(k.split('.')[2]) for k in state_dict.keys() if 'transformer.layers' in k]) + 1
        print(f"Detected architecture: hidden_dim={hidden_dim}, num_layers={num_layers}")
        
        self.model = CardTransformer(hidden_dim=hidden_dim, num_layers=num_layers, num_heads=8, dropout=0.0)
        self.model.load_state_dict(state_dict)
        self.model.eval()
        self.model.to(device)
        
        # Enable inference optimizations
        if hasattr(torch, 'inference_mode'):
            self._inference_context = torch.inference_mode
        else:
            self._inference_context = torch.no_grad
    
    @torch.inference_mode()
    def batch_inference(self, states: List[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]) -> List[Tuple[np.ndarray, float]]:
        """
        Run batched inference on multiple game states.
        
        Args:
            states: List of (card_ids, card_features, mask) tuples
            
        Returns:
            List of (policy_probs, value) tuples
        """
        if not states:
            return []
        
        # Stack into batches
        c_ids_batch = torch.stack([s[0] for s in states]).to(self.device)
        c_feats_batch = torch.stack([s[1] for s in states]).to(self.device)
        mask_batch = torch.stack([s[2] for s in states]).to(self.device)
        
        # Single forward pass for entire batch
        policy_logits, values = self.model(c_ids_batch, c_feats_batch, mask_batch)
        
        # Convert to numpy for workers
        policy_probs = torch.softmax(policy_logits, dim=-1).cpu().numpy()
        values = values.cpu().numpy().flatten()
        
        return [(policy_probs[i], values[i]) for i in range(len(states))]


class GameWorker:
    """Manages a single game instance for vectorized execution."""
    
    def __init__(self, encoder: SequenceEncoder, deck_loader: MetaDeckLoader, worker_id: int):
        self.encoder = encoder
        self.deck_loader = deck_loader
        self.worker_id = worker_id
        self.available_decks = deck_loader.list_decks()
        
        # State
        self.game: Optional[Game] = None
        self.samples: List[Dict] = []
        self.turn_count = 0
        self.current_valid_actions: List[Dict] = []
        
        # Initialize first game
        self.reset()
    
    def reset(self):
        """Start a new game."""
        # Pick random decks
        key1 = random.choice(self.available_decks)
        key2 = random.choice(self.available_decks)
        deck1 = self.deck_loader.get_deck(key1)
        deck2 = self.deck_loader.get_deck(key2)
        
        # Setup game
        self.game = Game()
        p1 = Player("Alpha1", self.game)
        p1.player_class = deck1['class']
        p2 = Player("Alpha2", self.game)
        p2.player_class = deck2['class']
        
        def make_cards(d, p):
            cards = []
            for cid in d['cards']:
                c = create_card(cid, self.game)
                if c:
                    c.controller = p
                    c.zone = Zone.DECK
                    cards.append(c)
            return cards
        
        p1.deck = make_cards(deck1, p1)
        p2.deck = make_cards(deck2, p2)
        
        self.game.setup(p1, p2)
        self.game.start_mulligan()
        self.game.do_mulligan(p1, [])
        self.game.do_mulligan(p2, [])
        
        self.samples = []
        self.turn_count = 0
        self.current_valid_actions = []
    
    def get_state(self) -> Optional[Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
        """
        Get current encoded state.
        Returns None if game is over or needs reset.
        """
        if self.game.ended or self.turn_count >= 60:
            return None
        
        player = self.game.current_player
        
        # Get valid actions
        self.current_valid_actions = self._get_valid_actions(self.game, player)
        
        # Auto-end turn if no actions
        while not self.current_valid_actions and not self.game.ended:
            self.game.end_turn()
            self.turn_count += 1
            if self.turn_count >= 60:
                return None
            
            player = self.game.current_player
            self.current_valid_actions = self._get_valid_actions(self.game, player)
        
        if self.game.ended:
            return None
            
        # Encode state
        state_wrapper = GameStateWrapper(self.game, self.game.current_player_idx)
        try:
            return self.encoder.encode(state_wrapper)
        except:
            # If encoding fails, end turn and retry next call (or fail game)
            self.game.end_turn()
            self.turn_count += 1
            return None
    
    def step(self, policy_probs: np.ndarray) -> Optional[List[Dict]]:
        """
        Apply action based on policy.
        Returns list of game samples if game ended, else None.
        """
        if not self.current_valid_actions:
            return None
            
        player = self.game.current_player
        
        # Select action
        action = self._select_action(policy_probs, self.current_valid_actions, player)
        
        # Record sample
        label = self._get_action_index(action, player)
        state_wrapper = GameStateWrapper(self.game, self.game.current_player_idx)
        try:
            c_ids, c_feats, mask = self.encoder.encode(state_wrapper)
            self.samples.append({
                'card_ids': c_ids.tolist(),
                'card_features': c_feats.tolist(),
                'action_label': label,
                'player_idx': self.game.current_player_idx
            })
        except:
            pass # Skip recording if encoding fails
            
        # Execute action
        self._execute_action(self.game, action)
        if action['type'] == 'END_TURN':
            self.turn_count += 1
            
        # Check game end
        if self.game.ended or self.turn_count >= 60:
            return self._finalize_game()
            
        return None
        
    def _finalize_game(self) -> List[Dict]:
        """Calculate outcomes and return samples."""
        winner_idx = self.game.players.index(self.game.winner) if self.game.winner else -1
        final_samples = []
        
        for sample in self.samples:
            p_idx = sample['player_idx']
            if winner_idx == -1:
                outcome = 0.0
            else:
                outcome = 1.0 if p_idx == winner_idx else -1.0
            
            final_samples.append({
                'card_ids': sample['card_ids'],
                'card_features': sample['card_features'],
                'action_label': sample['action_label'],
                'game_outcome': outcome
            })
        
        # Reset for next game
        self.reset()
        return final_samples

    def _get_valid_actions(self, game, player) -> List[Dict]:
        actions = []
        for card in player.hand:
            if player.can_play_card(card):
                actions.append({'type': 'PLAY', 'card': card})
        for minion in player.board:
            if minion.can_attack():
                for t in player.get_valid_attack_targets(minion):
                    actions.append({'type': 'ATTACK', 'attacker': minion, 'target': t})
        actions.append({'type': 'END_TURN'})
        return actions
    
    def _select_action(self, policy_probs: np.ndarray, valid_actions: List[Dict], player) -> Dict:
        valid_indices = []
        action_map = {}
        
        for act in valid_actions:
            idx = self._get_action_index(act, player)
            valid_indices.append(idx)
            action_map[idx] = act
        
        # Get probs for valid actions only
        probs = policy_probs[valid_indices]
        probs = probs / (probs.sum() + 1e-8)
        
        try:
            chosen_idx = np.random.choice(len(valid_indices), p=probs)
            return action_map[valid_indices[chosen_idx]]
        except:
            return random.choice(valid_actions)
    
    def _get_action_index(self, action: Dict, player) -> int:
        if action['type'] == 'PLAY':
            try:
                return player.hand.index(action['card'])
            except:
                return 0
        elif action['type'] == 'ATTACK':
            if action['attacker'] == player.hero:
                return 18
            try:
                return 11 + player.board.index(action['attacker'])
            except:
                return 11
        elif action['type'] == 'HERO_POWER':
            return 10
        elif action['type'] == 'END_TURN':
            return 19
        return 0
    
    def _execute_action(self, game, action: Dict):
        if action['type'] == 'PLAY':
            game.play_card(action['card'], action.get('target'))
        elif action['type'] == 'ATTACK':
            game.attack(action['attacker'], action['target'])
        elif action['type'] == 'HERO_POWER':
            game.use_hero_power(action.get('target'))
        elif action['type'] == 'END_TURN':
            game.end_turn()


class AlphaZeroGenerator:
    """GPU-optimized self-play generator with batched inference."""
    
    def __init__(self, output_file: str, model_path: str, batch_size: int = 32, 
                 num_workers: int = 4, data_dir: str = "data"):
        self.output_file = output_file
        self.batch_size = batch_size
        self.num_workers = num_workers
        
        # Get device
        self.device = get_device()
        print(f"Using device: {self.device}")
        
        # Load card database
        self.db = CardDatabase.get_instance()
        self.db.load()
        
        # Load meta decks
        self.deck_loader = MetaDeckLoader(data_dir)
        if not self.deck_loader.load():
            raise RuntimeError("Failed to load meta decks")
        
        # Initialize inference server
        self.inference_server = InferenceServer(model_path, self.device, batch_size)
        
        # Create encoder for workers
        self.encoder = SequenceEncoder()
        
        self.buffer = []
        self.games_played = 0
        self.games_failed = 0
    
    def generate_games(self, num_games: int):
        """Generate games using batched inference and vectorized workers."""
        print(f"Starting GPU-optimized AlphaZero generation of {num_games} games...")
        print(f"Batch size: {self.batch_size}, Workers: {self.num_workers}")
        
        # Initialize workers
        workers = [
            GameWorker(self.encoder, self.deck_loader, i) 
            for i in range(self.num_workers)
        ]
        
        # Track timing
        start_time = time.time()
        
        while self.games_played < num_games:
            # 1. Collect states from all active workers
            states = []
            active_worker_indices = []
            
            for i, worker in enumerate(workers):
                state = worker.get_state()
                if state is not None:
                    states.append(state)
                    active_worker_indices.append(i)
                else:
                    # If state is None (game ended/error), reset happens inside step or get_state usually,
                    # but if get_state returns None it means it just reset or turn loop limit reached.
                    # We should check if it has samples to finalize or just reset.
                    # Actually get_state returns None if game ended. 
                    # We need to make sure we don't get stuck.
                    # Simplified: if get_state is None, force reset or just continue (it might have auto-reset)
                    # Implementation detail: get_state returns None if game ended. 
                    # If game ended, we should have processed it in previous step.
                    # If it's a fresh game, it should return state.
                    # Safe fallback: reset if stuck
                    if worker.game.ended:
                        worker.reset()
            
            if not states:
                continue
                
            # 2. Run batched inference
            results = self.inference_server.batch_inference(states)
            
            # 3. Step workers with results
            for idx, (policy, _) in zip(active_worker_indices, results):
                worker = workers[idx]
                try:
                    samples = worker.step(policy)
                    if samples:
                        # Game finished
                        self.buffer.extend(samples)
                        self.games_played += 1
                        
                        # Progress update
                        if self.games_played % 10 == 0:
                            elapsed = time.time() - start_time
                            speed = self.games_played / elapsed if elapsed > 0 else 0
                            print(f"[{self.games_played}/{num_games}] Samples: {len(self.buffer)} "
                                  f"({speed:.1f} games/sec)")
                        
                        if self.games_played >= num_games:
                            break
                            
                except Exception as e:
                    print(f"Worker {idx} error: {e}")
                    worker.reset()
                    self.games_failed += 1
        
        # Save results
        self._save_buffer()
        
        elapsed = time.time() - start_time
        print(f"\nCompleted: {self.games_played} games in {elapsed:.1f}s")
        print(f"Total samples: {len(self.buffer)}")
        print(f"Speed: {self.games_played/elapsed:.2f} games/sec")
    
    def _save_buffer(self):
        Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)
        data = {'samples': self.buffer}
        with open(self.output_file, 'w') as f:
            json.dump(data, f)
        print(f"Saved to {self.output_file}")


# Keep old ModelAgent for compatibility
class ModelAgent:
    """Legacy agent for single-game inference."""
    
    def __init__(self, model_path: str, device: str = None, simulations: int = 50):
        if device is None:
            self.device = get_device()
        else:
            self.device = torch.device(device)
        
        self.simulations = simulations
        
        if os.path.exists(model_path):
            print(f"Loading model from {model_path}...")
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
            state_dict = checkpoint.get('model_state_dict', checkpoint)
            
            hidden_dim = state_dict['cls_token'].shape[-1]
            num_layers = max([int(k.split('.')[2]) for k in state_dict.keys() if 'transformer.layers' in k]) + 1
            
            self.model = CardTransformer(hidden_dim=hidden_dim, num_layers=num_layers, num_heads=8, dropout=0.0)
            self.model.load_state_dict(state_dict)
        else:
            self.model = CardTransformer(hidden_dim=256, num_layers=6, num_heads=8, dropout=0.0)
        
        self.model.eval()
        self.model.to(self.device)
        self.encoder = SequenceEncoder()
    
    def select_action(self, game: Game, valid_actions: List[Dict]) -> Dict:
        if not valid_actions:
            return None
        return self._select_action_policy(game, valid_actions)
    
    def _select_action_policy(self, game: Game, valid_actions: List[Dict]) -> Dict:
        state_wrapper = GameStateWrapper(game, game.current_player_idx)
        c_ids, c_feats, mask = self.encoder.encode(state_wrapper)
        
        c_ids = c_ids.unsqueeze(0).to(self.device)
        c_feats = c_feats.unsqueeze(0).to(self.device)
        mask = mask.unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            policy_logits, value = self.model(c_ids, c_feats, mask)
        
        valid_indices = []
        action_map = {}
        
        for act in valid_actions:
            idx = self._get_action_index(act, game.current_player)
            valid_indices.append(idx)
            action_map[idx] = act
        
        probs = torch.softmax(policy_logits[0, valid_indices], dim=0).cpu().numpy()
        
        try:
            chosen_idx_idx = np.random.choice(len(valid_indices), p=probs)
            return action_map.get(valid_indices[chosen_idx_idx], valid_actions[0])
        except:
            return random.choice(valid_actions)
    
    def _get_action_index(self, action, player):
        if action['type'] == 'PLAY':
            try:
                return player.hand.index(action['card'])
            except:
                return 0
        elif action['type'] == 'ATTACK':
            if action['attacker'] == player.hero:
                return 18
            try:
                return 11 + player.board.index(action['attacker'])
            except:
                return 11
        elif action['type'] == 'HERO_POWER':
            return 10
        elif action['type'] == 'END_TURN':
            return 19
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GPU-optimized AlphaZero self-play generator")
    parser.add_argument('--num-games', type=int, default=100, help='Number of games to generate')
    parser.add_argument('--output', type=str, default='data/alphazero_data.json', help='Output file')
    parser.add_argument('--model', type=str, required=True, help='Path to .pt model')
    parser.add_argument('--batch-size', type=int, default=32, help='Inference batch size')
    parser.add_argument('--workers', type=int, default=4, help='Number of parallel game workers')
    args = parser.parse_args()
    
    gen = AlphaZeroGenerator(
        args.output, 
        args.model,
        batch_size=args.batch_size,
        num_workers=args.workers
    )
    gen.generate_games(args.num_games)
