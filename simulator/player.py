"""Hearthstone Simulator - Player.

Manages player state: hero, hand, deck, board, mana, etc.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional, List, TYPE_CHECKING

from .enums import Zone, PlayState, Mulligan, CardType
from .entities import Entity, Card, Hero, HeroPower, Weapon, Minion

if TYPE_CHECKING:
    from .game import Game


class Player(Entity):
    """A player in the game."""
    
    MAX_HAND_SIZE: int = 10
    MAX_BOARD_SIZE: int = 7
    MAX_DECK_SIZE: int = 60
    STARTING_HAND_FIRST: int = 3
    STARTING_HAND_SECOND: int = 4
    MAX_MANA: int = 10
    
    def __init__(self, name: str = "Player", game: Optional[Game] = None):
        super().__init__(game)
        self.name: str = name
        
        # Hero
        self.hero: Optional[Hero] = None
        
        # Zones
        self.deck: List[Card] = []
        self.hand: List[Card] = []
        self.board: List[Minion] = []
        self.graveyard: List[Card] = []
        self.secrets: List[Card] = []
        
        # Mana
        self.mana_crystals: int = 0
        self.mana: int = 0
        self.overload: int = 0
        self.overload_next_turn: int = 0
        self.temp_mana: int = 0
        
        # State
        self.play_state: PlayState = PlayState.PLAYING
        self.mulligan_state: Mulligan = Mulligan.INVALID
        self.fatigue_counter: int = 0
        
        # History and Trackers
        self.cards_played_this_game: List[str] = []
        self.spells_played_this_game: List[str] = []
        self.minions_played_this_game_list: List[str] = []
        self.dead_minions: List[str] = []  # Graveyard (card IDs)
        self.cards_drawn_this_game: List[str] = []

    def clone(self) -> 'Player':
        """Create a deep copy of the player (excluding entities managed by Game.clone)."""
        new_player = Player(self.name, None)
        # Stats
        new_player.mana_crystals = self.mana_crystals
        new_player.mana = self.mana
        new_player.overload = self.overload
        new_player.overload_next_turn = self.overload_next_turn
        new_player.temp_mana = self.temp_mana
        new_player.play_state = self.play_state
        new_player.mulligan_state = self.mulligan_state
        new_player.fatigue_counter = self.fatigue_counter
        
        # History (Lists of strings/ints are safe to shallow copy if we create new list)
        new_player.cards_played_this_game = list(self.cards_played_this_game)
        new_player.spells_played_this_game = list(self.spells_played_this_game)
        new_player.minions_played_this_game_list = list(self.minions_played_this_game_list)
        new_player.dead_minions = list(self.dead_minions)
        new_player.cards_drawn_this_game = list(self.cards_drawn_this_game)
        
        # Custom attribs (like corpses, rafaams_played)
        # We should define a way to copy dynamic attributes.
        # For now, just copy specific known ones or __dict__?
        # __dict__ copy is safer for dynamic attributes
        for k, v in self.__dict__.items():
            if k not in ['hero', 'hero_power', 'deck', 'hand', 'board', 'graveyard', 'secrets', 'game', 'opponent', '_game']:
                if isinstance(v, (int, str, bool, float)) or v is None:
                    setattr(new_player, k, v)
                elif isinstance(v, list) and (not v or isinstance(v[0], (int, str))):
                     setattr(new_player, k, list(v))
                elif isinstance(v, set):
                     setattr(new_player, k, set(v))
                     
        return new_player
        self.damage_taken_this_turn: int = 0
        self.healing_taken_this_turn: int = 0
        
        # Current turn counters
        self.cards_played_this_turn: int = 0
        self.minions_played_this_turn: int = 0
        self.spells_played_this_turn: int = 0
        self.hero_power_uses_this_turn: int = 0
        
        # Status
        self.conceded: bool = False
        
        # Opponent reference
        self.opponent: Optional[Player] = None
    
    @property
    def spell_damage(self) -> int:
        """Calculate total spell damage from board."""
        total = 0
        for minion in self.board:
            total += minion.get_tag(GameTag.SPELLPOWER)
        return total

    @property
    def weapon(self) -> Optional[Weapon]:
        """Get the hero's weapon."""
        return self.hero.weapon if self.hero else None
    
    @property
    def hero_power(self) -> Optional[HeroPower]:
        """Get the hero's hero power."""
        return self.hero.hero_power if self.hero else None
    
    @property
    def health(self) -> int:
        """Get hero's current health."""
        return self.hero.health if self.hero else 0
    
    @property
    def armor(self) -> int:
        """Get hero's armor."""
        return self.hero.armor if self.hero else 0
    
    def add_to_deck(self, card: Card) -> bool:
        """Add a card to the deck."""
        if len(self.deck) >= self.MAX_DECK_SIZE:
            return False
        card.controller = self
        card.zone = Zone.DECK
        self.deck.append(card)
        return True
    
    def shuffle_deck(self) -> None:
        """Shuffle the deck."""
        random.shuffle(self.deck)
    
    def draw_specific_card(self, card: Card) -> Optional[Card]:
        """Draw a specific card instance from the deck."""
        if card in self.deck:
            self.deck.remove(card)
            if len(self.hand) >= self.MAX_HAND_SIZE:
                card.zone = Zone.GRAVEYARD
                self.graveyard.append(card)
                return None
            else:
                card.zone = Zone.HAND
                self.hand.append(card)
                self.cards_drawn_this_game.append(card.card_id)
                return card
        return None

    def draw(self, count: int = 1) -> List[Card]:
        """Draw cards from deck."""
        drawn: List[Card] = []
        
        for _ in range(count):
            if not self.deck:
                # Fatigue damage
                self.fatigue_counter += 1
                if self.hero:
                    self.game.deal_damage(self.hero, self.fatigue_counter)
                continue
            
            card = self.deck.pop(0)
            
            if len(self.hand) >= self.MAX_HAND_SIZE:
                # Mill the card
                card.zone = Zone.GRAVEYARD
                self.graveyard.append(card)
            else:
                card.zone = Zone.HAND
                self.hand.append(card)
                self.cards_drawn_this_game.append(card.card_id)
                drawn.append(card)
        
        return drawn
    
    def add_to_hand(self, card: Card) -> bool:
        """Add a card to hand (not from deck)."""
        if len(self.hand) >= self.MAX_HAND_SIZE:
            card.zone = Zone.GRAVEYARD
            self.graveyard.append(card)
            return False
        
        card.controller = self
        card.zone = Zone.HAND
        self.hand.append(card)
        return True
    
    def remove_from_hand(self, card: Card) -> bool:
        """Remove a card from hand."""
        if card in self.hand:
            self.hand.remove(card)
            return True
        return False
    
    def discard(self, count: int = 1) -> List[Card]:
        """Discard random cards from hand."""
        discarded: List[Card] = []
        for _ in range(count):
            if not self.hand:
                break
            card = random.choice(self.hand)
            self.hand.remove(card)
            card.zone = Zone.GRAVEYARD
            self.graveyard.append(card)
            discarded.append(card)
            self.game.fire_event("on_card_discarded", self, card)
        return discarded
    
    def summon(self, minion: Minion, position: int = -1) -> bool:
        """Summon a minion to the board."""
        if len(self.board) >= self.MAX_BOARD_SIZE:
            return False
        
        if position < 0 or position > len(self.board):
            position = len(self.board)
        
        minion.controller = self
        minion.zone = Zone.PLAY
        minion.zone_position = position
        minion.exhausted = True  # Summoning sickness
        
        self.board.insert(position, minion)
        
        # Update positions
        for i, m in enumerate(self.board):
            m.zone_position = i
        
        return True
    
    def remove_from_board(self, minion: Minion) -> bool:
        """Remove a minion from board."""
        if minion in self.board:
            self.board.remove(minion)
            # Update positions
            for i, m in enumerate(self.board):
                m.zone_position = i
            return True
        return False
    
    def equip_weapon(self, weapon: Weapon) -> None:
        """Equip a weapon (destroys existing one)."""
        if self.hero:
            if self.hero.weapon:
                old_weapon = self.hero.weapon
                old_weapon.zone = Zone.GRAVEYARD
                self.graveyard.append(old_weapon)
            
            weapon.controller = self
            weapon.zone = Zone.PLAY
            self.hero.weapon = weapon
    
    def spend_mana(self, amount: int) -> bool:
        """Spend mana if available."""
        available = self.mana + self.temp_mana
        if available < amount:
            return False
        
        # Use temp mana first
        temp_used = min(self.temp_mana, amount)
        self.temp_mana -= temp_used
        amount -= temp_used
        
        self.mana -= amount
        return True
    
    def gain_mana_crystal(self, count: int = 1, filled: bool = True) -> None:
        """Gain mana crystals."""
        self.mana_crystals = min(self.MAX_MANA, self.mana_crystals + count)
        if filled:
            self.mana = min(self.mana_crystals, self.mana + count)
    
    def start_turn(self) -> None:
        """Called at the start of player's turn."""
        # Gain mana crystal
        self.mana_crystals = min(self.MAX_MANA, self.mana_crystals + 1)
        
        # Refresh mana
        self.mana = self.mana_crystals
        
        # Apply overload from last turn
        self.mana = max(0, self.mana - self.overload)
        self.overload = self.overload_next_turn
        self.overload_next_turn = 0
        
        # Reset temp mana
        self.temp_mana = 0
        
        # Reset hero power
        if self.hero_power:
            self.hero_power.reset_for_turn()
        
        # Unfreeze and refresh minions
        for minion in self.board:
            minion.exhausted = False
            minion.attacks_this_turn = 0
            if minion.frozen:
                minion.frozen = False
        
        # Reduce location cooldowns
        for minion in self.board:
            if minion.card_type == CardType.LOCATION:
                minion.reduce_cooldown()
        
        # Reset hero attacks
        if self.hero:
            self.hero.exhausted = False
            self.hero.attacks_this_turn = 0
        
        # Reset counters
        self.cards_played_this_turn = 0
        self.minions_played_this_turn = 0
        self.spells_played_this_turn = 0
        self.hero_power_uses_this_turn = 0
        
        # Draw a card
        self.draw(1)
    
    def end_turn(self) -> None:
        """Called at the end of player's turn."""
        # Stealth is removed when attacking, not at end of turn
        pass
    
    def can_play_card(self, card: Card) -> bool:
        """Check if a card can be played."""
        if card not in self.hand:
            return False
        
        available_mana = self.mana + self.temp_mana
        if card.cost > available_mana:
            return False
        
        # Check board space for minions
        if card.card_type == CardType.MINION:
            if len(self.board) >= self.MAX_BOARD_SIZE:
                return False
        
        return True
    
    def get_valid_targets(self, card: Card) -> List[Entity]:
        """Get valid targets for a card."""
        # Use custom target handler if available
        if self.game and card.card_id in self.game._target_handlers:
            return self.game._target_handlers[card.card_id](self.game, card)
            
        # Base implementation: all characters
        targets: List[Entity] = []
        
        # Add all characters as potential targets
        if self.hero:
            targets.append(self.hero)
        targets.extend(self.board)
        
        if self.opponent:
            if self.opponent.hero:
                targets.append(self.opponent.hero)
            targets.extend(self.opponent.board)
        
        return targets
    
    def get_valid_attack_targets(self, attacker: Card) -> List[Card]:
        """Get valid attack targets for an attacker."""
        if not self.opponent:
            return []
        
        targets: List[Card] = []
        
        # Check for taunt
        taunts = [m for m in self.opponent.board if m.taunt and not m.stealth]
        
        if taunts:
            # Must attack taunt minions
            targets = taunts
        else:
            # Can attack hero or any minion without stealth
            if self.opponent.hero and not self.opponent.hero.immune:
                targets.append(self.opponent.hero)
            targets.extend([m for m in self.opponent.board if not m.stealth])
        
        # Rush minions can't attack hero on first turn
        if attacker.rush and attacker.exhausted:
            targets = [t for t in targets if t.card_type != CardType.HERO]
        
        return targets
    
    def __repr__(self) -> str:
        return f"<Player '{self.name}' HP:{self.health} Mana:{self.mana}/{self.mana_crystals}>"
