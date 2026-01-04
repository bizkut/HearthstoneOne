"""
Integration Test: OpponentModel with Game Simulation.

Verifies that the OpponentModel correctly tracks opponent behavior
during an actual simulated game.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.opponent_model import OpponentModel, OpponentStrategyPredictor
from ai.game_wrapper import HearthstoneGame
from simulator.enums import CardType


class TestOpponentModelIntegration(unittest.TestCase):
    """Integration test running OpponentModel during a simulated game."""
    
    def test_track_opponent_during_game(self):
        """Play a game and verify opponent tracking updates correctly."""
        # Initialize game
        env = HearthstoneGame()
        env.reset(use_meta_decks=True, do_mulligan=True)
        
        # Initialize opponent model (we track from player 1's perspective)
        opponent_model = OpponentModel()
        
        max_turns = 30
        turn_count = 0
        cards_tracked = 0
        actions_tracked = 0
        
        while not env.is_game_over and turn_count < max_turns:
            current_player = env.current_player
            is_opponent_turn = (current_player != env.my_player)
            
            # Get valid actions
            valid_actions = env.get_valid_actions()
            if not valid_actions:
                env._game.end_turn()
                turn_count += 1
                continue
            
            # Pick a random action (simplified)
            import random
            action = random.choice(valid_actions)
            
            # Track opponent's actions
            if is_opponent_turn:
                if action.action_type.name == "PLAY_CARD":
                    # Track card played
                    if action.card_index is not None and action.card_index < len(current_player.hand):
                        card = current_player.hand[action.card_index]
                        # Use card entity_id as a proxy (or card_id if available)
                        card_id = getattr(card, 'dbf_id', 0) or getattr(card, 'entity_id', 0)
                        opponent_model.observe_card_played(card_id, card.cost)
                        cards_tracked += 1
                        
                elif action.action_type.name == "ATTACK":
                    # Track attack
                    target = action.target_index
                    if target == 0:  # Face attack (hero)
                        opponent_model.observe_attack(
                            OpponentStrategyPredictor.ACTION_ATTACK_FACE, 
                            damage=3  # Simplified
                        )
                    else:
                        opponent_model.observe_attack(
                            OpponentStrategyPredictor.ACTION_ATTACK_MINION,
                            damage=3
                        )
                    actions_tracked += 1
            
            # Execute action
            try:
                env.step(action)
            except Exception:
                # Some actions may fail, just end turn
                env._game.end_turn()
                
            if action.action_type.name == "END_TURN":
                turn_count += 1
        
        # Verify opponent model has state
        state = opponent_model.get_state_dict()
        
        print(f"\n--- Integration Test Results ---")
        print(f"Turns played: {turn_count}")
        print(f"Cards tracked: {cards_tracked}")
        print(f"Actions tracked: {actions_tracked}")
        print(f"Archetype prediction: {state['archetype']}")
        print(f"Strategy prediction: {state['strategy']}")
        print(f"Face damage recorded: {state['face_damage']}")
        
        # Basic assertions
        self.assertIsInstance(state['archetype'], str)
        self.assertIsInstance(state['strategy'], str)
        
        # Verify embedding generation works
        embedding = opponent_model.get_embedding()
        self.assertEqual(embedding.shape[0], 32)
        
    def test_clone_during_game(self):
        """Verify cloning works mid-game for MCTS."""
        env = HearthstoneGame()
        env.reset(use_meta_decks=True, do_mulligan=True)
        
        opponent_model = OpponentModel()
        
        # Simulate some tracking
        opponent_model.observe_card_played(1, 2)
        opponent_model.observe_attack(OpponentStrategyPredictor.ACTION_ATTACK_FACE, 5)
        
        # Clone
        cloned_model = opponent_model.clone()
        
        # Modify clone
        cloned_model.observe_card_played(2, 3)
        
        # Verify independence
        self.assertEqual(len(opponent_model.hand_tracker.cards_played), 1)
        self.assertEqual(len(cloned_model.hand_tracker.cards_played), 2)
        
        print("\n--- Clone Test Passed ---")


if __name__ == '__main__':
    unittest.main(verbosity=2)
