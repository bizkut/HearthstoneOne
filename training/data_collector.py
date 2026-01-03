"""
Data Collector for HearthstoneOne AI.

Runs self-play games using the MCTS agent and collects training data.
"""

import sys
import os
import torch
import numpy as np
import time
from typing import List, Tuple, Optional

# Path hacks (assuming run from root)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.model import HearthstoneModel
from ai.encoder import FeatureEncoder
from ai.mcts import MCTS
from ai.game_wrapper import HearthstoneGame
from ai.replay_buffer import ReplayBuffer
from ai.actions import Action
from simulator.game import Game
from simulator.enums import GamePhase


def _play_game_worker(args):
    """Worker function for parallel game collection."""
    mcts_sims, game_idx, model_state_dict, encoder = args
    
    # Recreate model in this process
    model = HearthstoneModel(input_dim=690, action_dim=200)
    model.load_state_dict(model_state_dict)
    model.eval()
    
    env = HearthstoneGame()
    state = env.reset(randomize_first=True)
    
    trajectory = []
    step_count = 0
    max_steps = 150
    
    while not env.is_game_over and step_count < max_steps:
        root_game_state = env.game.clone()
        mcts = MCTS(model, encoder, root_game_state, num_simulations=mcts_sims)
        mcts_probs = mcts.search(root_game_state)
        
        encoded_state = encoder.encode(env.get_state())
        p_id = 1 if env.current_player == env.game.players[0] else 2
        trajectory.append((encoded_state, mcts_probs, p_id))
        
        action_idx = np.random.choice(len(mcts_probs), p=mcts_probs)
        
        # Apply action
        action_obj = Action.from_index(action_idx)
        game = env.game
        player = env.current_player
        
        try:
            if action_obj.action_type.name == "END_TURN":
                game.end_turn()
            elif action_obj.action_type.name == "PLAY_CARD":
                if action_obj.card_index is not None and action_obj.card_index < len(player.hand):
                    card = player.hand[action_obj.card_index]
                    game.play_card(card, None)
            elif action_obj.action_type.name == "HERO_POWER":
                game.use_hero_power()
        except:
            pass
        
        step_count += 1
    
    winner = 0
    if env.game.winner:
        winner = 1 if env.game.winner == env.game.players[0] else 2
    
    return trajectory, winner

class DataCollector:
    def __init__(self, model: HearthstoneModel, buffer: ReplayBuffer):
        self.model = model
        self.buffer = buffer
        self.encoder = FeatureEncoder()
        
    def collect_games(self, num_games: int, mcts_sims: int = 25, num_workers: int = None):
        """
        Run self-play games and populate buffer.
        Uses multiprocessing for parallel game collection.
        """
        import multiprocessing as mp
        from functools import partial
        
        if num_workers is None:
            num_workers = min(mp.cpu_count(), num_games, 8)  # Cap at 8 workers
        
        print(f"Starting collection of {num_games} games with {mcts_sims} MCTS simulations per move...")
        print(f"Using {num_workers} parallel workers")
        
        start_time = time.time()
        
        if num_workers > 1:
            # Parallel collection
            with mp.Pool(processes=num_workers) as pool:
                args = [(mcts_sims, i, self.model.state_dict(), self.encoder) for i in range(num_games)]
                results = []
                
                for i, result in enumerate(pool.imap_unordered(_play_game_worker, args)):
                    trajectory, winner = result
                    self.buffer.add_game(trajectory, winner)
                    
                    elapsed = time.time() - start_time
                    avg_time = elapsed / (i + 1)
                    print(f"Game {i+1}/{num_games} completed. Winner: Player {winner}. Buffer size: {len(self.buffer)}. Avg Time/Game: {avg_time:.2f}s")
        else:
            # Sequential fallback
            for g in range(num_games):
                trajectory, winner = self._play_single_game(mcts_sims, game_idx=g)
                self.buffer.add_game(trajectory, winner)
                
                elapsed = time.time() - start_time
                avg_time = elapsed / (g + 1)
                print(f"Game {g+1}/{num_games} completed. Winner: Player {winner}. Buffer size: {len(self.buffer)}. Avg Time/Game: {avg_time:.2f}s")
            
    def _play_single_game(self, mcts_sims: int, game_idx: int) -> Tuple[List, int]:
        """Plays one game returning (trajectory, winner_id)."""
        env = HearthstoneGame()
        state = env.reset(randomize_first=True) # Randomizes who goes first
        
        trajectory = [] # (state_tensor, policy, player_id)
        
        # Game Loop
        step_count = 0
        max_steps = 150 # Prevent infinite loops
        
        while not env.is_game_over and step_count < max_steps:
            # Prepare MCTS
            # Helper to clone the exact underlying game state properly for MCTS root
            # Note: MCTS expects `game` object as root state currently per my tests
            root_game_state = env.game.clone()
            
            mcts = MCTS(self.model, self.encoder, root_game_state, num_simulations=mcts_sims)
            
            # Run MCTS to get policy
            # Note: mcts.search() expects the root state (Game object)
            mcts_probs = mcts.search(root_game_state)
            
            # Store data
            # We want to store the ENCODED state for training later
            encoded_state = self.encoder.encode(env.get_state())
            current_player_id = env.current_player.entity_id # Player 1 or 2? 
            # Entities have IDs. Players in game.players are index 0 and 1.
            # Winner detection uses specific IDs or indices.
            # game.players[0] is usually P1.
            # Let's map to 1 or 2.
            p_id = 1 if env.current_player == env.game.players[0] else 2
            
            trajectory.append((encoded_state, mcts_probs, p_id))
            
            # Pick action
            # Training: Sample from distribution (exploration)
            # Evaluation: Argmax
            # For data collection: Sample (temperature 1.0) usually
            action_idx = np.random.choice(len(mcts_probs), p=mcts_probs)
            
            # Execute action
            self._apply_action_to_env(env, action_idx)
            
            step_count += 1
            
        # Determine winner
        winner = 0
        if env.game.winner:
            winner = 1 if env.game.winner == env.game.players[0] else 2
            
        return trajectory, winner
    
    def _apply_action_to_env(self, env: HearthstoneGame, action_idx: int):
        """Translates index to execution on the real environment."""
        action_obj = Action.from_index(action_idx)
        game = env.game
        player = env.current_player
        
        # Logic similar to MCTS._apply_action but on real game
        try:
            if action_obj.action_type.name == "END_TURN":
                game.end_turn()
            elif action_obj.action_type.name == "PLAY_CARD":
                if action_obj.card_index is not None and action_obj.card_index < len(player.hand):
                    card = player.hand[action_obj.card_index]
                    target = None
                    # TODO: Target resolution (simplified for now)
                    game.play_card(card, target)
            elif action_obj.action_type.name == "HERO_POWER":
                game.use_hero_power()
            # Attack logic...
        except Exception as e:
            # Fallback if action fails (illegal move selected despite masking? or logic error)
            # print(f"Action failed: {e}")
            pass

if __name__ == "__main__":
    # Test script
    buffer = ReplayBuffer()
    model = HearthstoneModel(input_dim=690, action_dim=200)
    collector = DataCollector(model, buffer)
    collector.collect_games(2, mcts_sims=10)
    print("Collection test complete.")
