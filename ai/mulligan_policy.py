"""
Mulligan Policy Network for HearthstoneOne.

Learns optimal mulligan decisions based on:
- Starting hand cards
- Opponent class
- Deck archetype

Output: Keep probability for each card in hand.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass, field


# Number of Hearthstone classes (Mage, Warrior, etc.)
NUM_CLASSES = 11

# Maximum cards in starting hand (4 for coin, 3 for first)
MAX_MULLIGAN_CARDS = 4


@dataclass
class MulliganExample:
    """A single mulligan decision with outcome."""
    hand_cards: List[dict]  # List of card dicts (cost, attack, health, card_id)
    opponent_class: int  # Class index (0-10)
    player_class: int  # Player's class
    cards_kept: List[bool]  # Which cards were kept
    game_won: Optional[bool] = None  # Outcome (for learning)
    
    
@dataclass
class MulliganDataset:
    """Collection of mulligan examples for training."""
    examples: List[MulliganExample] = field(default_factory=list)
    
    def add(self, example: MulliganExample):
        self.examples.append(example)
    
    def clear(self):
        self.examples.clear()
    
    def __len__(self):
        return len(self.examples)


class MulliganEncoder:
    """Encodes mulligan state into tensor representation."""
    
    # Card feature dimensions
    CARD_DIM = 16  # cost, attack, health, card_type (4), keywords (9)
    
    def __init__(self):
        # Input: 4 cards * CARD_DIM + opponent_class (11) + player_class (11)
        self.input_dim = MAX_MULLIGAN_CARDS * self.CARD_DIM + NUM_CLASSES * 2
    
    def encode(self, hand_cards: list, opponent_class: int, player_class: int) -> torch.Tensor:
        """Encode mulligan state to tensor."""
        features = []
        
        # Encode each card in hand
        for i in range(MAX_MULLIGAN_CARDS):
            if i < len(hand_cards):
                features.extend(self._encode_card(hand_cards[i]))
            else:
                features.extend([0] * self.CARD_DIM)
        
        # Opponent class one-hot
        opp_class_onehot = [0] * NUM_CLASSES
        if 0 <= opponent_class < NUM_CLASSES:
            opp_class_onehot[opponent_class] = 1
        features.extend(opp_class_onehot)
        
        # Player class one-hot
        player_class_onehot = [0] * NUM_CLASSES
        if 0 <= player_class < NUM_CLASSES:
            player_class_onehot[player_class] = 1
        features.extend(player_class_onehot)
        
        return torch.tensor(features, dtype=torch.float32)
    
    def _encode_card(self, card) -> List[float]:
        """Encode a single card."""
        # Get attributes safely
        cost = getattr(card, 'cost', 0) if hasattr(card, 'cost') else card.get('cost', 0)
        attack = getattr(card, 'attack', 0) if hasattr(card, 'attack') else card.get('attack', 0)
        health = getattr(card, 'health', 0) if hasattr(card, 'health') else card.get('health', 0)
        
        # Normalize cost (0-10 range)
        cost_norm = min(cost, 10) / 10.0
        attack_norm = min(attack, 12) / 12.0
        health_norm = min(health, 12) / 12.0
        
        features = [cost_norm, attack_norm, health_norm]
        
        # Card type one-hot (minion, spell, weapon, hero)
        card_type = getattr(card, 'card_type', 0) if hasattr(card, 'card_type') else card.get('card_type', 0)
        type_onehot = [0, 0, 0, 0]
        if 0 <= card_type < 4:
            type_onehot[card_type] = 1
        features.extend(type_onehot)
        
        # Keywords (taunt, divine_shield, etc.) - placeholder
        features.extend([0] * 9)  # 9 common keywords
        
        return features


class MulliganPolicy(nn.Module):
    """
    Neural Network for mulligan decisions.
    
    Input: Encoded mulligan state
    Output: Keep probability for each of 4 cards
    """
    
    def __init__(self, input_dim: int = None, hidden_dim: int = 64):
        super().__init__()
        
        encoder = MulliganEncoder()
        self.input_dim = input_dim or encoder.input_dim
        self.hidden_dim = hidden_dim
        
        # Shared layers
        self.fc1 = nn.Linear(self.input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.dropout = nn.Dropout(0.1)
        
        # Output: 4 independent keep probabilities
        self.output = nn.Linear(hidden_dim, MAX_MULLIGAN_CARDS)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Encoded mulligan state [batch, input_dim]
            
        Returns:
            Keep probabilities [batch, 4]
        """
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        
        # Sigmoid for independent probabilities (not softmax - each card is independent)
        keep_probs = torch.sigmoid(self.output(x))
        
        return keep_probs
    
    def get_mulligan_decision(self, hand_cards: list, opponent_class: int, 
                               player_class: int, threshold: float = 0.5) -> List[bool]:
        """
        Get mulligan decision for a hand.
        
        Args:
            hand_cards: List of cards in hand
            opponent_class: Opponent's class index
            player_class: Player's class index
            threshold: Keep threshold (default 0.5)
            
        Returns:
            List of bools - True = keep, False = replace
        """
        encoder = MulliganEncoder()
        state = encoder.encode(hand_cards, opponent_class, player_class)
        
        with torch.no_grad():
            keep_probs = self.forward(state.unsqueeze(0)).squeeze(0)
        
        # Apply threshold
        decisions = []
        for i in range(len(hand_cards)):
            decisions.append(keep_probs[i].item() >= threshold)
        
        return decisions


class MulliganTrainer:
    """Trains the MulliganPolicy from game outcomes."""
    
    def __init__(self, policy: MulliganPolicy, lr: float = 1e-3):
        self.policy = policy
        self.encoder = MulliganEncoder()
        self.optimizer = torch.optim.Adam(policy.parameters(), lr=lr)
        self.dataset = MulliganDataset()
        
    def add_example(self, example: MulliganExample):
        """Add a training example."""
        self.dataset.add(example)
    
    def train_batch(self, batch_size: int = 32) -> float:
        """
        Train on a batch of examples.
        
        Returns:
            Average loss
        """
        if len(self.dataset) < batch_size:
            return 0.0
        
        # Sample batch
        indices = np.random.choice(len(self.dataset.examples), batch_size, replace=False)
        batch = [self.dataset.examples[i] for i in indices]
        
        # Prepare tensors
        states = []
        targets = []
        weights = []
        
        for ex in batch:
            state = self.encoder.encode(ex.hand_cards, ex.opponent_class, ex.player_class)
            states.append(state)
            
            # Target: 1.0 for kept cards that led to win, 0.0 for kept cards that led to loss
            # This is a simplified reward signal
            target = torch.zeros(MAX_MULLIGAN_CARDS)
            weight = torch.zeros(MAX_MULLIGAN_CARDS)
            
            for i, kept in enumerate(ex.cards_kept):
                if i < len(ex.cards_kept):
                    if ex.game_won is not None:
                        # Positive signal for winning, negative for losing
                        if kept:
                            target[i] = 1.0 if ex.game_won else 0.0
                        else:
                            target[i] = 0.0 if ex.game_won else 1.0
                        weight[i] = 1.0
            
            targets.append(target)
            weights.append(weight)
        
        states = torch.stack(states)
        targets = torch.stack(targets)
        weights = torch.stack(weights)
        
        # Forward pass
        self.optimizer.zero_grad()
        predictions = self.policy(states)
        
        # Binary cross-entropy loss with weights
        loss = F.binary_cross_entropy(predictions, targets, weight=weights)
        
        # Backward pass
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
    
    def save(self, path: str):
        """Save policy checkpoint."""
        torch.save({
            'model_state_dict': self.policy.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, path)
    
    def load(self, path: str):
        """Load policy checkpoint."""
        checkpoint = torch.load(path, weights_only=False)
        self.policy.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
