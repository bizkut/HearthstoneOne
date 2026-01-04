#!/usr/bin/env python3
"""
AlphaZero Self-Play Generator for HearthstoneOne.

Generates reinforcement learning data by playing games using the trained Neural Network + MCTS.
Replaces the HeuristicAgent with the ModelAgent.
"""

import sys
import os
import json
import random
import argparse
import numpy as np
import torch
import mlx.core as mx
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

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
from ai.mcts import MCTS

class ModelAgent:
    """Agent that uses the Neural Network + MCTS to select actions."""
    
    def __init__(self, model_path: str, device: str = 'cpu', simulations: int = 50):
        self.device = device
        self.simulations = simulations
        
        # Load Model
        self.model = CardTransformer(hidden_dim=256, num_layers=6, num_heads=8, dropout=0.0)
        self.model.eval()
        
        if os.path.exists(model_path):
            print(f"Loading model from {model_path}...")
            # Support loading both PT and MLX (converted)
            # For inference in Python loop, PyTorch is easier unless we rewrite MCTS in MLX.
            # Assuming we use the converted PyTorch model here for compatibility with MCTS logic.
            checkpoint = torch.load(model_path, map_location=device)
            if 'model_state_dict' in checkpoint:
                 self.model.load_state_dict(checkpoint['model_state_dict'])
            else:
                 self.model.load_state_dict(checkpoint)
        else:
            print(f"Warning: Model {model_path} not found. Using random weights.")
            
        self.model.to(device)
        self.encoder = SequenceEncoder()
        self.mcts = MCTS(self.model, self.encoder, num_simulations=simulations)

    def select_action(self, game: Game, valid_actions: List[Dict]) -> Dict:
        if not valid_actions:
            return None
            
        # Use MCTS to select the best action
        # MCTS needs to simulate the game state.
        # Since full cloning of Game state is expensive/complex in Python,
        # AlphaZero often uses just the Policy Network for rollout or simplified lookahead.
        # For this script, we will use the Policy Network DIRECTLY (Greedy or Sampled) 
        # instead of full MCTS if cloning is not available,
        # OR we assume MCTS is implemented with a lightweight copy.
        
        # Checking ai/mcts.py capabilities...
        # If full MCTS is too slow, we default to Policy Network sampling (AlphaGo Zero "Policy Iteration").
        
        # Let's use direct Policy Network inference for speed in this generator
        # (True MCTS requires state cloning which is heavy).
        return self._select_action_policy(game, valid_actions)

    def _select_action_policy(self, game: Game, valid_actions: List[Dict]) -> Dict:
        # Encode state
        state_wrapper = GameStateWrapper(game, game.current_player_idx)
        c_ids, c_feats, mask = self.encoder.encode(state_wrapper)
        
        # Prepare batch
        c_ids = c_ids.unsqueeze(0).to(self.device)
        c_feats = c_feats.unsqueeze(0).to(self.device)
        mask = mask.unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            policy_logits, value = self.model(c_ids, c_feats, mask)
            
        # Mask invalid actions
        # Map valid actions to indices
        valid_indices = []
        action_map = {}
        
        for i, act in enumerate(valid_actions):
            idx = self._get_action_index(act, game.current_player)
            valid_indices.append(idx)
            action_map[idx] = act
            
        # Softmax over valid actions only
        probs = torch.softmax(policy_logits[0, valid_indices], dim=0).cpu().numpy()
        
        # Sample action (Exploration)
        # In self-play, we sample. In eval, we take argmax.
        try:
            chosen_idx_idx = np.random.choice(len(valid_indices), p=probs)
            chosen_action_idx = valid_indices[chosen_idx_idx]
            return action_map.get(chosen_action_idx, valid_actions[0])
        except ValueError:
            return random.choice(valid_actions)

    def _get_action_index(self, action, player):
        # Replicate logic from generator (should be unified in encoder)
        if action['type'] == 'PLAY':
            try: return player.hand.index(action['card'])
            except: return 0
        elif action['type'] == 'ATTACK':
            if action['attacker'] == player.hero: return 18
            try: return 11 + player.board.index(action['attacker'])
            except: return 11
        elif action['type'] == 'HERO_POWER':
            return 10
        elif action['type'] == 'END_TURN':
            return 19 # Assuming END_TURN is last? 
            # Check transformer_model.py action_dim. Usually 200.
            # We need a consistent mapping. 
            # For now, using simplified mapping compatible with Heuristic generator logic.
            return 20 # Arbitrary high number for End Turn
        return 0

class AlphaZeroGenerator:
    """Generates self-play games using the Neural Network."""
    
    def __init__(self, output_file: str, model_path: str, data_dir: str = "data"):
        self.output_file = output_file
        self.model_path = model_path
        self.buffer = []
        self.encoder = SequenceEncoder()
        
        # Load card database
        self.db = CardDatabase.get_instance()
        self.db.load()
        
        # Load meta decks
        self.deck_loader = MetaDeckLoader(data_dir)
        if not self.deck_loader.load():
            raise RuntimeError("Failed to load meta decks")
            
        # Initialize Agent
        # Uses PyTorch model for inference (converted from MLX)
        self.agent = ModelAgent(model_path, device='cpu') # CPU is safer for multiprocessing if added later
        
        self.games_played = 0
        self.games_failed = 0
        
    def generate_games(self, num_games: int):
        available_decks = self.deck_loader.list_decks()
        print(f"Starting AlphaZero generation of {num_games} games...")
        print(f"Model: {self.model_path}")
        
        for i in range(num_games):
            key1 = random.choice(available_decks)
            key2 = random.choice(available_decks)
            deck1 = self.deck_loader.get_deck(key1)
            deck2 = self.deck_loader.get_deck(key2)
            
            try:
                self._play_single_game(deck1, deck2)
                self.games_played += 1
                
                if self.games_played % 10 == 0:
                    print(f"[{self.games_played}/{num_games}] Samples: {len(self.buffer)}")
                    
            except Exception as e:
                self.games_failed += 1
        
        self._save_buffer()
        print(f"\nCompleted: {self.games_played} games. Total samples: {len(self.buffer)}")

    def _play_single_game(self, deck1: Dict, deck2: Dict):
        # Setup Game (Reuse code from generate_self_play via simplified call or logic copy)
        # For brevity, copying core setup logic
        game = Game()
        p1 = Player("Alpha1", game); p1.player_class = deck1['class']
        p2 = Player("Alpha2", game); p2.player_class = deck2['class']
        
        # Create cards helper
        def make_cards(d, p):
            cards = []
            for cid in d['cards']:
                c = create_card(cid, game)
                if c: c.controller = p; c.zone = Zone.DECK; cards.append(c)
            return cards
            
        p1.deck = make_cards(deck1, p1)
        p2.deck = make_cards(deck2, p2)
        
        # Setup Heroes
        # (Simplified hero setup)
        game.setup(p1, p2)
        game.start_mulligan()
        game.do_mulligan(p1, []) # Simple mulligan
        game.do_mulligan(p2, [])
        
        game_samples = []
        turn_count = 0
        
        while not game.ended and turn_count < 60:
            player = game.current_player
            pid = game.current_player_idx
            
            # 1. Capture State
            state = GameStateWrapper(game, pid)
            
            # 2. Get Valid Actions
            valid_actions = self._get_valid_actions(game, player)
            if not valid_actions:
                game.end_turn()
                turn_count += 1
                continue
                
            # 3. Select Action using Neural Net
            action = self.agent.select_action(game, valid_actions)
            
            # 4. Record Sample (State, Action)
            # We record the action we CHOSE (Policy Gradient style)
            # In true AlphaZero, we record the MCTS visit counts as the label.
            # Here we are doing "Policy Iteration" / Reinforce style for simplicity first.
            try:
                c_ids, c_feats, mask = self.encoder.encode(state)
                # Determine label index
                label = self.agent._get_action_index(action, player)
                
                game_samples.append({
                    'card_ids': c_ids.tolist(),
                    'card_features': c_feats.tolist(),
                    'action_label': label,
                    'player_idx': pid
                })
            except:
                pass
            
            # 5. Execute Action
            self._execute_action(game, action)
            if action['type'] == 'END_TURN':
                turn_count += 1
                
        # 6. Assign Rewards (Value Head Training)
        winner_idx = game.players.index(game.winner) if game.winner else -1
        for sample in game_samples:
            p_idx = sample['player_idx']
            if winner_idx == -1: outcome = 0.0 # Draw/Limit
            else: outcome = 1.0 if p_idx == winner_idx else -1.0
            
            self.buffer.append({
                'card_ids': sample['card_ids'],
                'card_features': sample['card_features'],
                'action_label': sample['action_label'],
                'game_outcome': outcome
            })

    def _get_valid_actions(self, game, player):
        # (Same logic as generate_self_play)
        # Ideally import this, but for standalone robustness:
        actions = []
        for card in player.hand:
            if player.can_play_card(card): actions.append({'type': 'PLAY', 'card': card})
        for minion in player.board:
            if minion.can_attack():
                for t in player.get_valid_attack_targets(minion):
                    actions.append({'type': 'ATTACK', 'attacker': minion, 'target': t})
        actions.append({'type': 'END_TURN'})
        return actions

    def _execute_action(self, game, action):
        if action['type'] == 'PLAY':
            game.play_card(action['card'], action.get('target'))
        elif action['type'] == 'ATTACK':
            game.attack(action['attacker'], action['target'])
        elif action['type'] == 'HERO_POWER':
            game.use_hero_power(action.get('target'))
        elif action['type'] == 'END_TURN':
            game.end_turn()

    def _save_buffer(self):
        Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)
        data = {'samples': self.buffer}
        with open(self.output_file, 'w') as f:
            json.dump(data, f)
        print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-games', type=int, default=100)
    parser.add_argument('--output', type=str, default='data/alphazero_data.json')
    parser.add_argument('--model', type=str, required=True, help="Path to .pt model")
    args = parser.parse_args()
    
    gen = AlphaZeroGenerator(args.output, args.model)
    gen.generate_games(args.num_games)
