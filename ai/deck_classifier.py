"""
Deck Archetype Classifier

Classifies Hearthstone decks into archetypes based on cards seen.
Used to condition the AI policy on opponent's likely strategy.

Archetypes:
- Aggro: Fast, low-curve, face damage
- Midrange: Board control, tempo plays
- Control: Removal, late-game value
- Combo: Specific synergy-driven win conditions
- OTK: One-turn-kill combo decks
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import IntEnum


class DeckArchetype(IntEnum):
    """Deck archetype categories."""
    UNKNOWN = 0
    AGGRO = 1
    MIDRANGE = 2
    CONTROL = 3
    COMBO = 4
    OTK = 5


# Archetype keywords for heuristic classification
ARCHETYPE_KEYWORDS = {
    DeckArchetype.AGGRO: [
        'leper', 'wolfrider', 'bluegill', 'charge', 'arcane_golem',
        'southsea', 'flame_imp', 'voidwalker', 'murloc', 'pirate'
    ],
    DeckArchetype.CONTROL: [
        'brawl', 'flamestrike', 'twisting_nether', 'shield_slam',
        'equality', 'consecration', 'blizzard', 'deathwing', 'ysera'
    ],
    DeckArchetype.COMBO: [
        'auctioneer', 'preparation', 'inner_fire', 'divine_spirit',
        'malygos', 'alexstrasza', 'emperor_thaurissan', 'leeroy'
    ],
    DeckArchetype.OTK: [
        'exodia', 'mechathun', 'togwaggle', 'shudderwock',
        'quest', 'shirvallah', 'uther'
    ]
}


@dataclass
class ArchetypePrediction:
    """Result of archetype classification."""
    archetype: DeckArchetype
    confidence: float
    probabilities: Dict[DeckArchetype, float]


class DeckClassifier(nn.Module):
    """
    Neural network classifier for deck archetypes.
    
    Input: Sequence of card IDs seen from opponent
    Output: Probability distribution over archetypes
    """
    
    def __init__(self,
                 num_cards: int = 10000,
                 embedding_dim: int = 64,
                 hidden_dim: int = 128,
                 num_archetypes: int = 6):
        super().__init__()
        
        self.num_archetypes = num_archetypes
        self.embedding_dim = embedding_dim
        
        # Card embedding
        self.card_embedding = nn.Embedding(num_cards, embedding_dim, padding_idx=0)
        
        # Aggregation: attention-weighted pooling
        self.attention = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, num_archetypes)
        )
    
    def forward(self, card_ids: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            card_ids: [batch, seq_len] tensor of card IDs
            mask: [batch, seq_len] boolean mask (True = valid, False = padding)
        
        Returns:
            [batch, num_archetypes] logits
        """
        # Embed cards: [batch, seq, embed_dim]
        embeddings = self.card_embedding(card_ids)
        
        # Attention weights: [batch, seq, 1]
        attn_scores = self.attention(embeddings)
        
        # Mask padding
        if mask is not None:
            attn_scores = attn_scores.masked_fill(~mask.unsqueeze(-1), float('-inf'))
        
        attn_weights = F.softmax(attn_scores, dim=1)
        
        # Weighted sum: [batch, embed_dim]
        pooled = (embeddings * attn_weights).sum(dim=1)
        
        # Classify
        logits = self.classifier(pooled)
        return logits
    
    def predict(self, card_ids: torch.Tensor, mask: Optional[torch.Tensor] = None) -> ArchetypePrediction:
        """
        Predict archetype for a single deck.
        
        Args:
            card_ids: [seq_len] tensor of card IDs
            mask: Optional [seq_len] mask
        
        Returns:
            ArchetypePrediction with archetype and confidence
        """
        self.eval()
        with torch.no_grad():
            # Add batch dimension
            ids = card_ids.unsqueeze(0)
            m = mask.unsqueeze(0) if mask is not None else None
            
            logits = self.forward(ids, m)
            probs = F.softmax(logits, dim=-1).squeeze(0)
            
            # Get prediction
            confidence, pred_idx = probs.max(dim=0)
            archetype = DeckArchetype(pred_idx.item())
            
            # Build probability dict
            prob_dict = {
                DeckArchetype(i): probs[i].item()
                for i in range(self.num_archetypes)
            }
            
            return ArchetypePrediction(
                archetype=archetype,
                confidence=confidence.item(),
                probabilities=prob_dict
            )


class HeuristicClassifier:
    """
    Rule-based deck classifier as fallback.
    Uses keyword matching on card names.
    """
    
    def __init__(self, card_database: Optional[Dict[int, str]] = None):
        """
        Args:
            card_database: Mapping from card_id -> card_name (lowercase)
        """
        self.card_db = card_database or {}
    
    def classify(self, card_ids: List[int], mana_costs: Optional[List[int]] = None) -> ArchetypePrediction:
        """
        Classify deck based on heuristics.
        
        Args:
            card_ids: List of card IDs seen
            mana_costs: Optional list of mana costs for those cards
        
        Returns:
            ArchetypePrediction
        """
        if not card_ids:
            return ArchetypePrediction(
                archetype=DeckArchetype.UNKNOWN,
                confidence=0.0,
                probabilities={a: 0.0 for a in DeckArchetype}
            )
        
        # Get card names
        card_names = [self.card_db.get(cid, '').lower() for cid in card_ids]
        
        # Score each archetype
        scores = {a: 0.0 for a in DeckArchetype if a != DeckArchetype.UNKNOWN}
        
        for archetype, keywords in ARCHETYPE_KEYWORDS.items():
            for name in card_names:
                for keyword in keywords:
                    if keyword in name:
                        scores[archetype] += 1.0
        
        # Mana curve heuristic
        if mana_costs:
            avg_cost = sum(mana_costs) / len(mana_costs)
            if avg_cost <= 2.5:
                scores[DeckArchetype.AGGRO] += 2.0
            elif avg_cost >= 4.5:
                scores[DeckArchetype.CONTROL] += 2.0
            else:
                scores[DeckArchetype.MIDRANGE] += 1.0
        
        # Normalize to probabilities
        total = sum(scores.values()) + 1e-6
        probs = {a: s / total for a, s in scores.items()}
        probs[DeckArchetype.UNKNOWN] = 0.0
        
        # Get best
        best_archetype = max(scores, key=scores.get)
        confidence = probs[best_archetype]
        
        # Default to MIDRANGE if no strong signal
        if confidence < 0.2:
            best_archetype = DeckArchetype.MIDRANGE
            confidence = 0.3
        
        return ArchetypePrediction(
            archetype=best_archetype,
            confidence=confidence,
            probabilities=probs
        )


class MetaTracker:
    """
    Tracks opponent's deck during a game and updates archetype prediction.
    """
    
    def __init__(self, 
                 nn_classifier: Optional[DeckClassifier] = None,
                 heuristic_classifier: Optional[HeuristicClassifier] = None,
                 device: str = 'cpu'):
        self.nn_classifier = nn_classifier
        self.heuristic = heuristic_classifier or HeuristicClassifier()
        self.device = device
        
        # Game state
        self.seen_cards: List[int] = []
        self.seen_costs: List[int] = []
        self.current_prediction: Optional[ArchetypePrediction] = None
    
    def reset(self):
        """Reset for new game."""
        self.seen_cards = []
        self.seen_costs = []
        self.current_prediction = None
    
    def observe_card(self, card_id: int, mana_cost: int = 0):
        """
        Observe a card played by opponent.
        
        Args:
            card_id: ID of the card
            mana_cost: Mana cost of the card
        """
        if card_id not in self.seen_cards:
            self.seen_cards.append(card_id)
            self.seen_costs.append(mana_cost)
        
        # Update prediction
        self._update_prediction()
    
    def _update_prediction(self):
        """Update archetype prediction based on seen cards."""
        if not self.seen_cards:
            return
        
        # Try neural classifier first
        if self.nn_classifier is not None and len(self.seen_cards) >= 3:
            card_tensor = torch.tensor(self.seen_cards, device=self.device)
            self.current_prediction = self.nn_classifier.predict(card_tensor)
        else:
            # Fall back to heuristic
            self.current_prediction = self.heuristic.classify(
                self.seen_cards, self.seen_costs
            )
    
    def get_archetype(self) -> DeckArchetype:
        """Get current archetype prediction."""
        if self.current_prediction:
            return self.current_prediction.archetype
        return DeckArchetype.UNKNOWN
    
    def get_confidence(self) -> float:
        """Get confidence of current prediction."""
        if self.current_prediction:
            return self.current_prediction.confidence
        return 0.0
    
    def get_archetype_embedding(self, embedding_dim: int = 32) -> torch.Tensor:
        """
        Get learnable embedding vector for current archetype.
        Used as input to the main Transformer policy.
        
        Args:
            embedding_dim: Dimension of embedding vector
        
        Returns:
            [embedding_dim] tensor
        """
        archetype = self.get_archetype()
        confidence = self.get_confidence()
        
        # Simple one-hot scaled by confidence
        embedding = torch.zeros(len(DeckArchetype))
        embedding[archetype] = confidence
        
        # Project to desired dimension if needed
        if embedding_dim != len(DeckArchetype):
            # Linear projection (should use learned projection in practice)
            projection = torch.zeros(embedding_dim)
            projection[:len(DeckArchetype)] = embedding
            return projection
        
        return embedding
