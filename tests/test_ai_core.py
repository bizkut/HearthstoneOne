import unittest
import torch
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator.game import Game
from simulator.player import Player
from simulator.card_loader import create_card, CardDatabase
from simulator.enums import GamePhase
from ai.game_wrapper import HearthstoneGame
from ai.encoder import FeatureEncoder
from ai.model import HearthstoneModel
from ai.mcts import MCTS

class TestAICore(unittest.TestCase):
    
    def setUp(self):
        # Setup basic game
        self.game = Game()
        p1 = Player("P1")
        p2 = Player("P2")
        self.game.setup(p1, p2)
        p1.hero = create_card("HERO_08", self.game) # Mage
        p2.hero = create_card("HERO_01", self.game) # Warrior
        p1.hero.controller = p1
        p2.hero.controller = p2
        
        # Load DB
        CardDatabase.get_instance().load()

        # Add some cards
        c1 = create_card("CS2_023", self.game)
        added1 = p1.add_to_hand(c1) # Arcane Intellect
        print(f"Added Card 1: {added1}, Hand Size: {len(p1.hand)}")
        
        c2 = create_card("CS2_029", self.game)
        added2 = p1.add_to_hand(c2) # Fireball
        print(f"Added Card 2: {added2}, Hand Size: {len(p1.hand)}")
        
        p1.summon(create_card("CS2_182", self.game), 0) # Boulderfist Ogre
        
        self.wrapper = HearthstoneGame()
        self.wrapper._game = self.game
        
    def test_game_cloning(self):
        """Verify that Game.clone() creates a deep copy properly."""
        print("\nTesting Game Cloning...")
        
        # Find p1 in players (order may be randomized by setup)
        p1 = next(p for p in self.game.players if p.name == "P1")
        p1_idx = self.game.players.index(p1)
        
        print(f"Original Hand Size Pre-Clone: {len(p1.hand)}")
        
        clone = self.game.clone()
        
        # Modify original
        p1.mana = 99
        print(f"Original Hand Size Post-Clone: {len(p1.hand)}")
        self.assertTrue(len(p1.hand) > 0, "Player hand is empty")
        p1.hand[0].cost = 0
        
        # Check clone is untouched
        cloned_p1 = clone.players[p1_idx]
        self.assertEqual(cloned_p1.mana, 0, "Clone mana should not change")
        self.assertNotEqual(cloned_p1.hand[0].cost, 0, "Clone card cost should not change")
        
        # Verify entities are different objects
        self.assertIsNot(p1, cloned_p1)
        self.assertIsNot(p1.hand[0], cloned_p1.hand[0])
        self.assertIsNot(p1.board[0], cloned_p1.board[0])
        
        # Verify triggers are preserved (by count at least)
        # Note: Triggers are minimal in vanilla game without effects
        self.assertEqual(len(clone._triggers), len(self.game._triggers))

    def test_encoder(self):
        """Test State -> Tensor encoding."""
        print("\nTesting Feature Encoder...")
        encoder = FeatureEncoder()
        state = self.wrapper.get_state()
        tensor = encoder.encode(state)
        
        print(f"Encoded Shape: {tensor.shape}")
        self.assertEqual(len(tensor.shape), 1)
        self.assertEqual(tensor.shape[0], encoder.input_dim)
        
    def test_model_forward(self):
        """Test Neural Network forward pass."""
        print("\nTesting Model Forward Pass...")
        encoder = FeatureEncoder()
        model = HearthstoneModel(encoder.input_dim, action_dim=200) # Full action dim
        
        dummy_input = torch.randn(1, encoder.input_dim)
        policy, value = model(dummy_input)
        
        print(f"Policy Shape: {policy.shape}, Value: {value.item()}")
        self.assertEqual(policy.shape, (1, 200))
        self.assertEqual(value.shape, (1, 1))
        
    def test_mcts_search(self):
        """Test MCTS simulation iteration."""
        print("\nTesting MCTS Search...")
        encoder = FeatureEncoder()
        # Mock action dim = 200 (Enough for all actions)
        model = HearthstoneModel(encoder.input_dim, action_dim=200)
        mcts = MCTS(model, encoder, self.game.clone(), num_simulations=5)
        
        # Run search from current state
        # Note: MCTS expects a state object for root. MCTS.search uses `game_env.clone()` internally?
        # Actually MCTS.search takes `root_state`.
        # And `_expand` uses `encoder.encode(node.state)`.
        # `game_wrapper.GameState` is what we pass around or the `Game` object directly?
        # MCTS needs to simulate. 
        # For this test, let's fix MCTS usage:
        
        # In MCTS implementation step 1564:
        # root = MCTSNode(root_state)
        # _expand encodes root_state.
        
        # But MCTS needs a way to APPLY actions to get children states.
        # My current MCTS implementation in Step 1564 DOES NOT IMPLEMENT applying actions.
        # It just creates logic children but doesn't transition state in `_expand`:
        # "node.children[idx] = MCTSNode(state=None, parent=node, action_idx=idx)" 
        # It leaves state=None.
        
        # This confirms we need to finish MCTS logic to use the Simulator Clone.
        # But let's run what we have to see it fail or pass partial logic.
        
        # Try running search
        # Now MCTS logic should work with cloning
        state = self.game.clone() # Pass Game object as root
        # Or does MCTS expects GameState wrapper?
        # MCTS uses wrapper to get encoding.
        # But MCTSNode root expects 'state'. In our code:
        # root = MCTSNode(root_state)
        # _expand uses root_state as game_copy
        # So root_state SHOULD be a Game object.
        
        probs = mcts.search(state)
        print(f"MCTS Probs: {probs}")
        self.assertIsNotNone(probs)
        self.assertTrue(len(probs) > 0)

if __name__ == "__main__":
    unittest.main()
