"""Action representation for HearthstoneOne AI."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, List, Any


class ActionType(Enum):
    """Types of actions a player can take."""
    PLAY_CARD = auto()       # Play a card from hand
    ATTACK = auto()          # Attack with minion or hero
    HERO_POWER = auto()      # Use hero power
    END_TURN = auto()        # End the current turn
    CHOOSE = auto()          # Choose an option (discover, etc.)
    MULLIGAN = auto()        # Mulligan selection


@dataclass
class Action:
    """
    Represents a single game action.
    
    Attributes:
        action_type: Type of action
        card_index: Index of card in hand (for PLAY_CARD)
        attacker_index: Index of attacking minion (-1 for hero)
        target_index: Index of target (-1 for hero, None for no target)
        target_is_friendly: Whether target is friendly
        choice_index: Index for CHOOSE actions
        position: Board position for minion placement
    """
    action_type: ActionType
    card_index: Optional[int] = None
    attacker_index: Optional[int] = None
    target_index: Optional[int] = None
    target_is_friendly: bool = False
    choice_index: Optional[int] = None
    position: Optional[int] = None
    
    # Reference to the actual Fireplace action (for execution)
    _fp_action: Any = None
    
    @classmethod
    def play_card(cls, card_index: int, target_index: Optional[int] = None,
                  target_is_friendly: bool = False, position: int = 0) -> "Action":
        """Create a PLAY_CARD action."""
        return cls(
            action_type=ActionType.PLAY_CARD,
            card_index=card_index,
            target_index=target_index,
            target_is_friendly=target_is_friendly,
            position=position,
        )
    
    @classmethod
    def attack(cls, attacker_index: int, target_index: int,
               target_is_friendly: bool = False) -> "Action":
        """
        Create an ATTACK action.
        
        Args:
            attacker_index: Index of attacker on board (-1 for hero)
            target_index: Index of target (-1 for enemy hero)
            target_is_friendly: Whether attacking own minion (rare cases)
        """
        return cls(
            action_type=ActionType.ATTACK,
            attacker_index=attacker_index,
            target_index=target_index,
            target_is_friendly=target_is_friendly,
        )
    
    @classmethod
    def hero_power(cls, target_index: Optional[int] = None,
                   target_is_friendly: bool = False) -> "Action":
        """Create a HERO_POWER action."""
        return cls(
            action_type=ActionType.HERO_POWER,
            target_index=target_index,
            target_is_friendly=target_is_friendly,
        )
    
    @classmethod
    def end_turn(cls) -> "Action":
        """Create an END_TURN action."""
        return cls(action_type=ActionType.END_TURN)
    
    @classmethod
    def choose(cls, choice_index: int) -> "Action":
        """Create a CHOOSE action for discover/options."""
        return cls(
            action_type=ActionType.CHOOSE,
            choice_index=choice_index,
        )
    
    @classmethod
    def mulligan(cls, card_indices: List[int]) -> "Action":
        """
        Create a MULLIGAN action.
        
        Args:
            card_indices: Indices of cards to mulligan (replace)
        """
        # Encode as single action with indices in card_index
        return cls(
            action_type=ActionType.MULLIGAN,
            choice_index=sum(1 << i for i in card_indices),  # Bitmask
        )
    
    def to_index(self, max_hand: int = 10, max_board: int = 7) -> int:
        """
        Convert action to a unique integer index for the neural network.
        
        Action space layout:
        - 0: END_TURN
        - 1-10: HERO_POWER (0 = no target, 1-7 = enemy minions, 8 = enemy hero, 9 = friendly)
        - 11-110: PLAY_CARD (10 cards * 10 targets each)
        - 111-174: ATTACK (8 attackers * 8 targets)
        
        Total: ~175 actions (simplified, actual may vary)
        """
        if self.action_type == ActionType.END_TURN:
            return 0
        
        elif self.action_type == ActionType.HERO_POWER:
            base = 1
            if self.target_index is None:
                return base
            elif self.target_is_friendly:
                return base + 9
            elif self.target_index == -1:  # Enemy hero
                return base + 8
            else:
                return base + 1 + self.target_index
        
        elif self.action_type == ActionType.PLAY_CARD:
            base = 11
            card_offset = (self.card_index or 0) * 10
            if self.target_index is None:
                target_offset = 0
            elif self.target_index == -1:  # Enemy hero
                target_offset = 8
            elif self.target_is_friendly:
                target_offset = 9
            else:
                target_offset = 1 + (self.target_index or 0)
            return base + card_offset + target_offset
        
        elif self.action_type == ActionType.ATTACK:
            base = 111
            attacker_offset = ((self.attacker_index or 0) + 1) * 8  # +1 because -1 = hero
            if self.target_index == -1:  # Enemy hero
                target_offset = 0
            else:
                target_offset = 1 + (self.target_index or 0)
            return base + attacker_offset + target_offset
        
        return 0
    
    @classmethod
    def from_index(cls, index: int) -> "Action":
        """
        Convert an integer index back to an Action.
        
        This is the inverse of to_index().
        """
        if index == 0:
            return cls.end_turn()
        
        elif 1 <= index <= 10:
            offset = index - 1
            if offset == 0:
                return cls.hero_power()
            elif offset == 8:
                return cls.hero_power(target_index=-1)
            elif offset == 9:
                return cls.hero_power(target_index=0, target_is_friendly=True)
            else:
                return cls.hero_power(target_index=offset - 1)
        
        elif 11 <= index <= 110:
            offset = index - 11
            card_index = offset // 10
            target_offset = offset % 10
            if target_offset == 0:
                return cls.play_card(card_index)
            elif target_offset == 8:
                return cls.play_card(card_index, target_index=-1)
            elif target_offset == 9:
                return cls.play_card(card_index, target_index=0, target_is_friendly=True)
            else:
                return cls.play_card(card_index, target_index=target_offset - 1)
        
        elif 111 <= index <= 174:
            offset = index - 111
            attacker_index = (offset // 8) - 1  # -1 converts back to hero = -1
            target_offset = offset % 8
            if target_offset == 0:
                return cls.attack(attacker_index, target_index=-1)
            else:
                return cls.attack(attacker_index, target_index=target_offset - 1)
        
        return cls.end_turn()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "type": self.action_type.name,
            "card_index": self.card_index,
            "attacker_index": self.attacker_index,
            "target_index": self.target_index,
            "target_is_friendly": self.target_is_friendly,
            "choice_index": self.choice_index,
            "position": self.position,
        }
    
    def __repr__(self) -> str:
        if self.action_type == ActionType.END_TURN:
            return "Action(END_TURN)"
        elif self.action_type == ActionType.HERO_POWER:
            target = f" -> {self.target_index}" if self.target_index is not None else ""
            return f"Action(HERO_POWER{target})"
        elif self.action_type == ActionType.PLAY_CARD:
            target = f" -> {self.target_index}" if self.target_index is not None else ""
            return f"Action(PLAY_CARD[{self.card_index}]{target})"
        elif self.action_type == ActionType.ATTACK:
            return f"Action(ATTACK[{self.attacker_index}] -> {self.target_index})"
        elif self.action_type == ActionType.CHOOSE:
            return f"Action(CHOOSE[{self.choice_index}])"
        return f"Action({self.action_type.name})"


# Action space constants
ACTION_SPACE_SIZE = 175  # Total number of possible action indices
