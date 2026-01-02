"""
Evaluation Script for HearthstoneOne AI.

Compare different agents against each other:
1. Model (MCTS) vs Random
2. Model (Current) vs Model (Best/Old)
"""

import sys
import os
import torch
import numpy as np
import time
from typing import Tuple

# Path hacks
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.model import HearthstoneModel
from ai.encoder import FeatureEncoder
from ai.mcts import MCTS
from ai.game_wrapper import HearthstoneGame
from ai.actions import Action

class Arena:
    def __init__(self, model_path: str = None, device="cpu"):
        self.device = device
        self.encoder = FeatureEncoder()
        
        # Load model 1 (The Challenger)
        self.model = HearthstoneModel(input_dim=690, action_dim=200).to(self.device)
        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=device))
            print(f"Loaded challenger model from {model_path}")
        else:
            print("Warning: No model path provided or file not found. Using untrained model.")
        
        self.model.eval()

    def play_games(self, num_games: int, mcts_sims: int = 10) -> Tuple[int, int, int]:
        """
        Play num_games: Model vs Random.
        Model plays as Player 1 in half games, Player 2 in other half?
        For simplicity: Model is ALWAYS Player 1 (index 0) vs Random as Player 2.
        
        Returns: (model_wins, random_wins, draws)
        """
        print(f"Starting Arena: Model vs Random ({num_games} games)...")
        
        wins = 0
        losses = 0
        draws = 0
        
        start_time = time.time()
        
        for g in range(num_games):
            env = HearthstoneGame()
            # To be fair, usually flip coins.
            # But let's verify if Model can beat Random when going first.
            env.reset(randomize_first=False) 
            # randomize_first=False means P1 (index 0) usually goes first?
            # Or depends on game logic.
            # In our game engine, players[0] is initialized as current usually.
            
            # Game Loop
            step = 0
            while not env.is_game_over and step < 200:
                current_player_idx = 0 if env.current_player == env.game.players[0] else 1
                # print(f"Turn {step}, Player {current_player_idx}") # Debug
                
                if current_player_idx == 0:
                    # === MODEL TURN (Player 1) ===
                    # Use MCTS
                    root_state = env.game.clone()
                    mcts = MCTS(self.model, self.encoder, root_state, num_simulations=mcts_sims) # mcts_sims passed from arg
                    probs = mcts.search(root_state)
                    
                    # Greedy action for evaluation
                    action_idx = np.argmax(probs)
                    
                    self._apply_action(env, action_idx)
                    
                else:
                    # === RANDOM TURN (Player 2) ===
                    valid_actions = env.get_valid_actions()
                    if not valid_actions:
                        # Should not happen as End Turn is always valid?
                        # If truly no actions, pass
                        env.game.end_turn()
                    else:
                        random_action = np.random.choice(valid_actions)
                        
                        # Apply simulator action directly? 
                        # Or convert to index and back to test wrapper?
                        # Using wrapper apply directly on object
                        self._apply_action_object(env, random_action)
                        
                step += 1
                
            # Result
            if env.game.winner == env.game.players[0]:
                wins += 1
                result = "WIN"
            elif env.game.winner == env.game.players[1]:
                losses += 1
                result = "LOSS"
            else:
                draws += 1
                result = "DRAW"
                
            print(f"Game {g+1}: {result} | Model Win Rate: {wins/(g+1):.2%} (Steps: {step})")
                 
        return wins, losses, draws

    def _apply_action(self, env, action_idx):
        from ai.actions import Action
        action_obj = Action.from_index(action_idx)
        self._execute(env, action_obj, "Model")

    def _apply_action_object(self, env, action_obj):
        self._execute(env, action_obj, "Random")
        
    def _execute(self, env, action, player_name):
         game = env.game
         player = env.current_player
         
         try:
             if action.action_type.name == "END_TURN":
                game.end_turn()
                # print(f"[{player_name}] End Turn")
                
             elif action.action_type.name == "PLAY_CARD":
                 if action.card_index is not None and action.card_index < len(player.hand):
                     card = player.hand[action.card_index]
                     # Simplified Target Logic: Default to enemy hero if needed
                     target = None
                     if card.requires_target:
                         # Try to find enemy hero first
                         enemy_hero = player.opponent.hero
                         target = enemy_hero
                     
                     game.play_card(card, target)
                     # print(f"[{player_name}] Played {card.name}")
                     
             elif action.action_type.name == "HERO_POWER":
                 if player.hero_power.can_use():
                     game.use_hero_power()
                 
             elif action.action_type.name == "ATTACK":
                 # Identify attacker
                 attacker = None
                 # Simplification: In Action logic, attackers are indexed.
                 # Let's assume we attack with EVERYTHING capable efficiently?
                 # OR rely on Action object properties if implemented
                 
                 # Fallback for Random Agent loop which returns Simulator Actions directly:
                 if hasattr(action, 'source'):
                     attacker = action.source
                     target = action.target
                     if attacker and target:
                         game.attack(attacker, target)
                         # print(f"[{player_name}] Attack {attacker} -> {target}")
                         
         except Exception as e:
            # print(f"Action Failed for {player_name}: {e}")
            pass

if __name__ == "__main__":
    # Test Evaluation
    # Try to load latest checkpoint if exists
    checkpoint = "models/checkpoint_iter_2.pt"
    if not os.path.exists(checkpoint):
        checkpoint = None
        
    arena = Arena(model_path=checkpoint)
    arena.play_games(num_games=2, mcts_sims=2) 
