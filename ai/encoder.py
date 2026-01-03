import numpy as np
import torch
from .game_state import GameState
from .actions import ACTION_SPACE_SIZE

class FeatureEncoder:
    """
    Encodes the GameState into a tensor representation suitable for Neural Networks.
    
    Representation typically includes:
    - Scalar features (Mana, Health, Deck Size, Hand Size)
    - Board features (Minion stats, keywords)
    - Hand features (Card costs, types)
    - Hero features
    - History features
    """
    
    def __init__(self):
        # Define dimensions
        self.scalar_dim = 10 # Mana, Max Mana, Health P1, Health P2, Deck1, Deck2, Hand1, Hand2, Graveyard1, Graveyard2
        self.card_dim = 20 # Cost, Attack, Health, Type (one-hot), Keywords (one-hot), etc.
        self.max_hand = 10
        self.max_board = 7
        self.input_dim = self.scalar_dim + (self.max_hand * 2 * self.card_dim) + (self.max_board * 2 * self.card_dim) 
        # Note: This is a simplified dense representation. 
        # A Transformer would take a sequence of cards.
        
    def encode(self, state: GameState) -> torch.Tensor:
        """Encodes state to tensor."""
        # 1. Scalars
        scalars = [
            state.friendly_player.mana,
            state.friendly_player.max_mana,
            state.friendly_player.hero.health,
            state.enemy_player.hero.health,
            state.friendly_player.deck_size,
            state.enemy_player.deck_size,
            len(state.friendly_player.hand),
            len(state.enemy_player.hand), # Note: enemy hand is list of unknowns usually, but length is known
            state.friendly_player.fatigue,
            state.enemy_player.fatigue,
        ]
        
        # 2. Hand Cards (My hand only - Opponent hand is hidden/unknown mostly)
        # For simplicity in this version, we zero-pad opponent hand features or use known info if available
        # Ideally we mask unknown information.
        
        hand_features = []
        # Clamp to max_hand to prevent dimension overflow
        hand_to_encode = state.friendly_player.hand[:self.max_hand]
        for card in hand_to_encode:
            hand_features.extend(self._encode_card(card))
        # Pad remaining slots
        padding = [0] * self.card_dim * (self.max_hand - len(hand_to_encode))
        hand_features.extend(padding)
        
        # Opponent hand (Placeholder/Unknown)
        opp_hand_features = [0] * self.card_dim * self.max_hand 
        
        # 3. Board Minions (clamp to max_board)
        board_features = []
        board_to_encode = state.friendly_player.board[:self.max_board]
        for minion in board_to_encode:
            board_features.extend(self._encode_card(minion))
        padding = [0] * self.card_dim * (self.max_board - len(board_to_encode))
        board_features.extend(padding)
        
        opp_board_features = []
        opp_board_to_encode = state.enemy_player.board[:self.max_board]
        for minion in opp_board_to_encode:
            opp_board_features.extend(self._encode_card(minion))
        padding = [0] * self.card_dim * (self.max_board - len(opp_board_to_encode))
        opp_board_features.extend(padding)
        
        # Combine
        full_vector = scalars + hand_features + opp_hand_features + board_features + opp_board_features
        
        return torch.tensor(full_vector, dtype=torch.float32)

    def _encode_card(self, card_data) -> list:
        """Helper to encode a single card."""
        # This takes a dictionary or object relative to game_state.py structures
        # Looking at game_state.py, hand/board are lists of dicts or objects?
        # game_wrapper.py converts them.
        
        # Assuming card_data is a dictionary or object with attributes:
        # cost, attack, health, type, etc.
        
        # Safe access
        cost = getattr(card_data, 'cost', 0)
        attack = getattr(card_data, 'attack', 0)
        health = getattr(card_data, 'health', 0)
        
        features = [cost, attack, health]
        
        # Placeholder for one-hot encoding types/keywords
        # Fill rest to card_dim
        features.extend([0] * (self.card_dim - len(features)))
        return features

    @property
    def observation_shape(self):
        return (self.input_dim,)
