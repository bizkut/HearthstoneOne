"""
Unit tests for Opponent Modeling (Phase 8).
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.opponent_model import (
    OpponentHandTracker, 
    OpponentStrategyPredictor, 
    OpponentModel,
    StrategyType
)
from ai.deck_classifier import DeckArchetype


class TestOpponentHandTracker(unittest.TestCase):
    
    def setUp(self):
        # Simple card database for testing
        self.card_db = {
            1: {'name': 'Leper Gnome', 'cost': 1},
            2: {'name': 'Flame Imp', 'cost': 1},
            3: {'name': 'Brawl', 'cost': 5},
            4: {'name': 'Flamestrike', 'cost': 7},
            5: {'name': 'Azure Drake', 'cost': 5},
        }
        self.tracker = OpponentHandTracker(self.card_db)
    
    def test_reset(self):
        self.tracker.observe_card_played(1, 1)
        self.tracker.reset()
        self.assertEqual(len(self.tracker.cards_played), 0)
        self.assertEqual(self.tracker.hand_size, 0)
    
    def test_observe_card_played(self):
        self.tracker.hand_size = 4
        self.tracker.observe_card_played(1, 1)
        self.assertEqual(len(self.tracker.cards_played), 1)
        self.assertEqual(self.tracker.hand_size, 3)
    
    def test_set_archetype_updates_priors(self):
        self.tracker.set_archetype(DeckArchetype.AGGRO)
        self.assertEqual(self.tracker.archetype, DeckArchetype.AGGRO)
    
    def test_get_hand_probabilities(self):
        self.tracker.set_archetype(DeckArchetype.AGGRO)
        probs = self.tracker.get_hand_probabilities(5)
        # Should return a list
        self.assertIsInstance(probs, list)


class TestOpponentStrategyPredictor(unittest.TestCase):
    
    def setUp(self):
        self.predictor = OpponentStrategyPredictor()
    
    def test_reset(self):
        self.predictor.observe_action(OpponentStrategyPredictor.ACTION_ATTACK_FACE, 5)
        self.predictor.reset()
        self.assertEqual(len(self.predictor.action_history), 0)
        self.assertEqual(self.predictor.damage_dealt_to_face, 0)
    
    def test_aggressive_prediction(self):
        # Simulate aggressive behavior - lots of face attacks
        for _ in range(5):
            self.predictor.observe_action(
                OpponentStrategyPredictor.ACTION_ATTACK_FACE, 
                damage=3
            )
        
        prediction = self.predictor.predict_strategy()
        self.assertEqual(prediction.strategy, StrategyType.AGGRESSIVE)
        self.assertGreater(prediction.confidence, 0.3)
    
    def test_defensive_prediction(self):
        # Simulate defensive behavior - lots of trading
        for _ in range(5):
            self.predictor.observe_action(
                OpponentStrategyPredictor.ACTION_ATTACK_MINION, 
                damage=3
            )
        
        prediction = self.predictor.predict_strategy()
        self.assertEqual(prediction.strategy, StrategyType.DEFENSIVE)
    
    def test_board_centric_prediction(self):
        # Simulate board development
        for _ in range(5):
            self.predictor.observe_action(OpponentStrategyPredictor.ACTION_PLAY_MINION)
        
        prediction = self.predictor.predict_strategy()
        self.assertEqual(prediction.strategy, StrategyType.BOARD_CENTRIC)


class TestOpponentModel(unittest.TestCase):
    
    def setUp(self):
        self.card_db = {
            1: {'name': 'Leper Gnome', 'cost': 1},
            2: {'name': 'Flame Imp', 'cost': 1},
        }
        self.model = OpponentModel(card_database=self.card_db)
    
    def test_reset(self):
        self.model.observe_card_played(1, 1)
        self.model.reset()
        self.assertEqual(len(self.model.meta_tracker.seen_cards), 0)
    
    def test_observe_card_played(self):
        self.model.observe_card_played(1, 1)
        self.assertEqual(len(self.model.meta_tracker.seen_cards), 1)
    
    def test_observe_attack(self):
        self.model.observe_attack(target_is_face=True, damage=5)
        self.assertEqual(self.model.strategy_predictor.damage_dealt_to_face, 5)
    
    def test_get_embedding(self):
        embedding = self.model.get_embedding()
        self.assertEqual(embedding.shape[0], 32)
    
    def test_get_state_dict(self):
        state = self.model.get_state_dict()
        self.assertIn('archetype', state)
        self.assertIn('strategy', state)
        self.assertIn('face_damage', state)


if __name__ == '__main__':
    unittest.main()
