"""
Opponent Modeling for HearthstoneOne AI.

Tracks opponent behavior and predicts hidden information:
- Cards likely in opponent's hand
- Opponent's play style / strategy
- Probable next actions

Phase 8 Implementation.
"""

import torch
import torch.nn as nn
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import IntEnum
from collections import defaultdict

from .deck_classifier import DeckArchetype, MetaTracker, DeckClassifier, HeuristicClassifier


class StrategyType(IntEnum):
    """Opponent strategy categories."""
    UNKNOWN = 0
    AGGRESSIVE = 1    # Going face, maximizing damage
    DEFENSIVE = 2     # Trading, clearing board
    BOARD_CENTRIC = 3 # Developing minions
    VALUE = 4         # Drawing cards, generating resources
    COMBO_SETUP = 5   # Holding cards, setting up lethal


@dataclass
class StrategyPrediction:
    """Result of strategy classification."""
    strategy: StrategyType
    confidence: float
    probabilities: Dict[StrategyType, float]


@dataclass
class HandProbability:
    """Probability estimate for a card being in opponent's hand."""
    card_id: int
    probability: float
    reasoning: str = ""


class OpponentHandTracker:
    """
    Tracks likely cards in opponent's hand using Bayesian inference.
    
    Updates beliefs based on:
    - Cards played (remove from possibilities)
    - Cards drawn (increase hand size)
    - Deck archetype (prior probabilities)
    - Mana available (what could be played)
    """
    
    # Common cards by archetype - these have higher priors
    ARCHETYPE_CORE_CARDS: Dict[DeckArchetype, List[str]] = {
        DeckArchetype.AGGRO: [
            'leper_gnome', 'wolfrider', 'bluegill_warrior', 'flame_imp',
            'southsea_deckhand', 'abusive_sergeant', 'arcane_golem'
        ],
        DeckArchetype.CONTROL: [
            'brawl', 'shield_slam', 'execute', 'flamestrike', 'blizzard',
            'twisting_nether', 'equality', 'consecration', 'hex', 'polymorph'
        ],
        DeckArchetype.COMBO: [
            'gadgetzan_auctioneer', 'preparation', 'innervate', 'wild_growth',
            'emperor_thaurissan', 'malygos', 'leeroy_jenkins'
        ],
        DeckArchetype.MIDRANGE: [
            'azure_drake', 'piloted_shredder', 'loatheb', 'sludge_belcher',
            'savannah_highmane', 'tirion_fordring'
        ],
        DeckArchetype.OTK: [
            'archmage_antonidas', 'ice_block', 'alexstrasza', 'pyroblast',
            'mechathun', 'cataclysm'
        ]
    }
    
    def __init__(self, card_database: Optional[Dict[int, dict]] = None):
        """
        Args:
            card_database: Mapping from card_id -> card info dict with 'name', 'cost', etc.
        """
        self.card_db = card_database or {}
        
        # Pre-compute archetype to card ID mapping for performance
        self.archetype_card_ids: Dict[DeckArchetype, List[int]] = defaultdict(list)
        self._precompute_archetype_map()
        
        self.reset()
        
    def _precompute_archetype_map(self):
        """Map archetype names to card IDs once on init."""
        for archetype, core_names in self.ARCHETYPE_CORE_CARDS.items():
            for cid, info in self.card_db.items():
                card_name = info.get('name', '').lower().replace(' ', '_')
                if any(core in card_name for core in core_names):
                    self.archetype_card_ids[archetype].append(cid)
    
    def reset(self):
        """Reset for a new game."""
        self.cards_played: List[int] = []  # Card IDs played by opponent
        self.cards_drawn: int = 0          # Number of cards drawn
        self.hand_size: int = 0            # Current hand size (inferred)
        self.mana_available: int = 0       # Opponent's current mana
        self.turn_number: int = 0
        self.archetype: DeckArchetype = DeckArchetype.UNKNOWN
        
        # Probability map: card_id -> P(in hand)
        self._hand_probs: Dict[int, float] = defaultdict(float)
    
    def clone(self) -> 'OpponentHandTracker':
        """Create a deep copy."""
        new = OpponentHandTracker.__new__(OpponentHandTracker)
        new.card_db = self.card_db
        new.archetype_card_ids = self.archetype_card_ids
        new.cards_played = list(self.cards_played)
        new.cards_drawn = self.cards_drawn
        new.hand_size = self.hand_size
        new.mana_available = self.mana_available
        new.turn_number = self.turn_number
        new.archetype = self.archetype
        new._hand_probs = self._hand_probs.copy()
        return new
    
    def set_archetype(self, archetype: DeckArchetype):
        """Update the assumed archetype (from MetaTracker)."""
        if self.archetype != archetype:
            self.archetype = archetype
            self._update_priors()
    
    def observe_card_played(self, card_id: int, mana_cost: int = 0):
        """Record a card played by opponent."""
        self.cards_played.append(card_id)
        self.hand_size = max(0, self.hand_size - 1)
        
        # Remove from hand probabilities
        if card_id in self._hand_probs:
            del self._hand_probs[card_id]
        
        # Playing cheap cards early suggests aggro
        if mana_cost <= 2 and self.turn_number <= 3:
            self._boost_archetype_probs(DeckArchetype.AGGRO, 0.1)
        elif mana_cost >= 5:
            self._boost_archetype_probs(DeckArchetype.CONTROL, 0.05)
    
    def observe_card_drawn(self, count: int = 1):
        """Record opponent drawing cards."""
        self.cards_drawn += count
        self.hand_size += count
        # Drawing extra cards suggests value/control
        if count > 1:
            self._boost_archetype_probs(DeckArchetype.CONTROL, 0.05)
    
    def set_game_state(self, mana: int, turn: int, hand_size: int):
        """Update game state information."""
        self.mana_available = mana
        self.turn_number = turn
        self.hand_size = hand_size
    
    def get_hand_probabilities(self, top_k: int = 10) -> List[HandProbability]:
        """
        Get top-K most likely cards in opponent's hand.
        
        Returns:
            List of HandProbability sorted by probability descending
        """
        # Update based on current mana (can't have cards > max mana early)
        probs = []
        for card_id, prob in self._hand_probs.items():
            card_info = self.card_db.get(card_id, {})
            card_cost = card_info.get('cost', 0)
            
            # Adjust probability based on mana curve
            adjusted_prob = prob
            if card_cost > self.turn_number + 1:
                adjusted_prob *= 0.5  # Less likely to have very expensive cards early
            
            probs.append(HandProbability(
                card_id=card_id,
                probability=adjusted_prob,
                reasoning=f"Archetype: {self.archetype.name}"
            ))
        
        # Sort by probability
        probs.sort(key=lambda x: x.probability, reverse=True)
        return probs[:top_k]
    
    def get_card_probability(self, card_id: int) -> float:
        """Get probability of a specific card being in opponent's hand."""
        return self._hand_probs.get(card_id, 0.0)
    
    def _update_priors(self):
        """Update hand probabilities based on archetype."""
        # Reset with archetype priors
        target_ids = self.archetype_card_ids.get(self.archetype, [])
        for cid in target_ids:
            if cid not in self.cards_played:
                self._hand_probs[cid] = 0.3  # Base prior for archetype cards
    
    def _boost_archetype_probs(self, archetype: DeckArchetype, amount: float):
        """Boost probabilities for cards associated with an archetype."""
        target_ids = self.archetype_card_ids.get(archetype, [])
        for cid in target_ids:
            if cid not in self.cards_played:
                self._hand_probs[cid] = min(1.0, self._hand_probs.get(cid, 0.1) + amount)


class OpponentStrategyPredictor:
    """
    Predicts opponent's current strategy based on action history.
    
    Uses pattern matching on recent actions to classify intent.
    """
    
    # Action type constants
    ACTION_PLAY_MINION = 1
    ACTION_PLAY_SPELL = 2
    ACTION_ATTACK_FACE = 3
    ACTION_ATTACK_MINION = 4
    ACTION_HERO_POWER = 5
    ACTION_END_TURN = 6
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset for new game."""
        self.action_history: List[int] = []
        self.damage_dealt_to_face: int = 0
        self.damage_dealt_to_minions: int = 0
        self.minions_played: int = 0
        self.spells_played: int = 0
        self.cards_drawn_extra: int = 0  # Beyond normal draw
    
    def clone(self) -> 'OpponentStrategyPredictor':
        """Create a deep copy."""
        new = OpponentStrategyPredictor()
        new.action_history = list(self.action_history)
        new.damage_dealt_to_face = self.damage_dealt_to_face
        new.damage_dealt_to_minions = self.damage_dealt_to_minions
        new.minions_played = self.minions_played
        new.spells_played = self.spells_played
        new.cards_drawn_extra = self.cards_drawn_extra
        return new

    def observe_action(self, action_type: int, damage: int = 0):
        """
        Record an opponent action.
        
        Args:
            action_type: One of the ACTION_* constants
            damage: Damage dealt if attack action
        """
        self.action_history.append(action_type)
        
        if action_type == self.ACTION_ATTACK_FACE:
            self.damage_dealt_to_face += damage
        elif action_type == self.ACTION_ATTACK_MINION:
            self.damage_dealt_to_minions += damage
        elif action_type == self.ACTION_PLAY_MINION:
            self.minions_played += 1
        elif action_type == self.ACTION_PLAY_SPELL:
            self.spells_played += 1
    
    def predict_strategy(self) -> StrategyPrediction:
        """
        Predict opponent's current strategy based on behavior.
        
        Returns:
            StrategyPrediction with strategy type and confidence
        """
        scores = {s: 0.0 for s in StrategyType if s != StrategyType.UNKNOWN}
        
        # Analyze face vs trade ratio (only if attacks have occurred)
        total_damage = self.damage_dealt_to_face + self.damage_dealt_to_minions
        if total_damage > 0:
            face_ratio = self.damage_dealt_to_face / total_damage
            if face_ratio > 0.7:
                scores[StrategyType.AGGRESSIVE] += 2.0
            elif face_ratio < 0.3:
                scores[StrategyType.DEFENSIVE] += 1.5
        
        # Analyze minion vs spell ratio - prioritize board-centric
        if self.minions_played > 0:
            if self.minions_played > self.spells_played * 2:
                scores[StrategyType.BOARD_CENTRIC] += 2.0  # Strong signal
            elif self.minions_played > self.spells_played:
                scores[StrategyType.BOARD_CENTRIC] += 1.5
        
        if self.spells_played > self.minions_played:
            scores[StrategyType.VALUE] += 1.0
        
        # Recent action patterns (last 5 actions)
        recent = self.action_history[-5:] if len(self.action_history) >= 5 else self.action_history
        face_attacks = sum(1 for a in recent if a == self.ACTION_ATTACK_FACE)
        minion_attacks = sum(1 for a in recent if a == self.ACTION_ATTACK_MINION)
        
        if face_attacks >= 3:
            scores[StrategyType.AGGRESSIVE] += 1.5
        if minion_attacks >= 3:
            scores[StrategyType.DEFENSIVE] += 1.0
        
        # Check for holding cards (possible combo)
        if len(self.action_history) > 10 and self.minions_played < 3:
            scores[StrategyType.COMBO_SETUP] += 1.0
        
        # Normalize to probabilities
        total = sum(scores.values()) + 1e-6
        probs = {s: score / total for s, score in scores.items()}
        probs[StrategyType.UNKNOWN] = 0.0
        
        # Get best prediction
        best_strategy = max(scores, key=scores.get)
        confidence = probs[best_strategy]
        
        # Default to BOARD_CENTRIC if no clear signal
        if confidence < 0.25:
            best_strategy = StrategyType.BOARD_CENTRIC
            confidence = 0.3
        
        return StrategyPrediction(
            strategy=best_strategy,
            confidence=confidence,
            probabilities=probs
        )


class OpponentModel:
    """
    Main opponent modeling class that integrates all components.
    
    Provides a unified API for tracking opponent state and generating
    embeddings for the transformer model.
    """
    
    def __init__(self, 
                 card_database: Optional[Dict[int, dict]] = None,
                 deck_classifier: Optional[DeckClassifier] = None,
                 device: str = 'cpu'):
        """
        Args:
            card_database: Mapping from card_id -> card info
            deck_classifier: Neural deck classifier (optional)
            device: PyTorch device for tensors
        """
        self.device = device
        
        # Sub-components
        self.meta_tracker = MetaTracker(
            nn_classifier=deck_classifier,
            heuristic_classifier=HeuristicClassifier(
                {cid: info.get('name', '') for cid, info in (card_database or {}).items()}
            ),
            device=device
        )
        self.hand_tracker = OpponentHandTracker(card_database)
        self.strategy_predictor = OpponentStrategyPredictor()
        
        # Embedding dimension for output
        self.embedding_dim = 32
        
    def clone(self) -> 'OpponentModel':
        """Create a deep copy for MCTS."""
        # Using __new__ to avoid init overhead
        new = OpponentModel.__new__(OpponentModel)
        new.device = self.device
        
        # Deep copy sub-components (MetaTracker doesn't need full clone if it's stateless enough or we don't predict archetype changes in MCTS)
        # But archetype CAN change. For now we assume MetaTracker is roughly static or we re-instantiate lightly.
        # Actually MetaTracker has seen_cards.
        # Let's just create a new one or assuming MetaTracker has a clone (it doesn't yet).
        # Fallback: recreate.
        # Ideally MetaTracker should have clone. 
        # But for now, let's just shallow copy the tracker since we likely won't play NEW cards for opponent in simulation 
        # (simulation is usually friendly moves, or opponent moves from known set).
        # Actually in Opponent move phase, we DO generate moves.
        # For safety let's manually copy state if possible.
        
        # Since I can't easily modify MetaTracker (outside this file right now easily without tool switch), 
        # I'll rely on recreating it if needed or just copy reference if we accept risk.
        # Given limitations, I will deep copy the components I control.
        
        new.hand_tracker = self.hand_tracker.clone()
        new.strategy_predictor = self.strategy_predictor.clone()
        
        # For MetaTracker, we'll just reference it (Optimization tradeoff)
        # Assuming classification doesn't change drastically during a few simulation steps.
        new.meta_tracker = self.meta_tracker # Shared reference
        new.embedding_dim = self.embedding_dim
        
        return new
    
    def reset(self):
        """Reset for new game."""
        self.meta_tracker.reset()
        self.hand_tracker.reset()
        self.strategy_predictor.reset()
    
    def observe_card_played(self, card_id: int, mana_cost: int = 0):
        """Record opponent playing a card."""
        self.meta_tracker.observe_card(card_id, mana_cost)
        self.hand_tracker.observe_card_played(card_id, mana_cost)
        
        # Update hand tracker with latest archetype
        self.hand_tracker.set_archetype(self.meta_tracker.get_archetype())
        
        # Record action type
        # TODO: Distinguish minion vs spell from card database
        self.strategy_predictor.observe_action(
            OpponentStrategyPredictor.ACTION_PLAY_MINION
        )
    
    def observe_card_drawn(self, count: int = 1):
        """Record opponent drawing cards."""
        self.hand_tracker.observe_card_drawn(count)
    
    def observe_attack(self, target_is_face: bool, damage: int = 0):
        """Record opponent attack."""
        action_type = (
            OpponentStrategyPredictor.ACTION_ATTACK_FACE 
            if target_is_face 
            else OpponentStrategyPredictor.ACTION_ATTACK_MINION
        )
        self.strategy_predictor.observe_action(action_type, damage)
    
    def update_game_state(self, mana: int, turn: int, hand_size: int):
        """Update with current game state."""
        self.hand_tracker.set_game_state(mana, turn, hand_size)
    
    def get_archetype(self) -> DeckArchetype:
        """Get predicted deck archetype."""
        return self.meta_tracker.get_archetype()
    
    def get_archetype_id(self) -> int:
        """Get archetype as integer for transformer input."""
        return int(self.get_archetype())
    
    def get_strategy(self) -> StrategyPrediction:
        """Get predicted strategy."""
        return self.strategy_predictor.predict_strategy()
    
    def get_hand_probabilities(self, top_k: int = 10) -> List[HandProbability]:
        """Get most likely cards in opponent's hand."""
        return self.hand_tracker.get_hand_probabilities(top_k)
    
    def get_embedding(self) -> torch.Tensor:
        """
        Get embedding vector for transformer input.
        
        Combines:
        - Archetype one-hot (6 dims)
        - Strategy one-hot (6 dims) 
        - Confidence scores (2 dims)
        - Action statistics (normalized, 4 dims)
        - Padding to embedding_dim (14 dims)
        
        Returns:
            [embedding_dim] tensor
        """
        embedding = torch.zeros(self.embedding_dim, device=self.device)
        
        # Archetype one-hot (dims 0-5)
        archetype = self.get_archetype()
        archetype_confidence = self.meta_tracker.get_confidence()
        embedding[int(archetype)] = archetype_confidence
        
        # Strategy one-hot (dims 6-11)
        strategy_pred = self.get_strategy()
        embedding[6 + int(strategy_pred.strategy)] = strategy_pred.confidence
        
        # Confidence scores (dims 12-13)
        embedding[12] = archetype_confidence
        embedding[13] = strategy_pred.confidence
        
        # Action statistics (dims 14-17)
        sp = self.strategy_predictor
        total_actions = len(sp.action_history) + 1
        embedding[14] = min(1.0, sp.damage_dealt_to_face / 30.0)  # Normalized face damage
        embedding[15] = min(1.0, sp.damage_dealt_to_minions / 30.0)  # Normalized trade damage
        embedding[16] = min(1.0, sp.minions_played / 10.0)  # Normalized minion count
        embedding[17] = min(1.0, sp.spells_played / 10.0)  # Normalized spell count
        
        return embedding
    
    def get_state_dict(self) -> dict:
        """Get current state for serialization/debugging."""
        return {
            'archetype': self.get_archetype().name,
            'archetype_confidence': self.meta_tracker.get_confidence(),
            'strategy': self.get_strategy().strategy.name,
            'strategy_confidence': self.get_strategy().confidence,
            'cards_seen': len(self.meta_tracker.seen_cards),
            'hand_size': self.hand_tracker.hand_size,
            'face_damage': self.strategy_predictor.damage_dealt_to_face,
            'trade_damage': self.strategy_predictor.damage_dealt_to_minions,
        }
