"""Hearthstone Simulator - Game Entities.

Defines all game entities: Cards, Minions, Heroes, Weapons, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable, TYPE_CHECKING
from abc import ABC, abstractmethod

from .enums import Zone, CardType, CardClass, Rarity, Race, SpellSchool, GameTag

if TYPE_CHECKING:
    from .game import Game
    from .player import Player


@dataclass
class CardData:
    """Static card data loaded from CardDefs."""
    card_id: str
    name: str = ""
    text: str = ""
    card_set: str = "UNKNOWN"
    cost: int = 0
    attack: int = 0
    health: int = 0
    armor: int = 0
    durability: int = 0
    card_type: CardType = CardType.INVALID
    card_class: CardClass = CardClass.NEUTRAL
    rarity: Rarity = Rarity.FREE
    race: Race = Race.INVALID
    spell_school: SpellSchool = SpellSchool.NONE
    collectible: bool = False
    
    # Keywords (boolean flags)
    taunt: bool = False
    divine_shield: bool = False
    charge: bool = False
    windfury: bool = False
    stealth: bool = False
    poisonous: bool = False
    lifesteal: bool = False
    rush: bool = False
    reborn: bool = False
    battlecry: bool = False
    deathrattle: bool = False
    secret: bool = False
    discover: bool = False
    outcast: bool = False
    # New keywords (synced from python-hearthstone)
    echo: bool = False
    magnetic: bool = False
    overkill: bool = False
    twinspell: bool = False
    spellburst: bool = False
    corrupt: bool = False
    dormant: bool = False
    frenzy: bool = False
    tradeable: bool = False
    infuse: bool = False
    colossal: bool = False
    titan: bool = False
    forge: bool = False
    
    # Extra data
    tags: Dict[int, int] = field(default_factory=dict)


class Entity:
    """Base class for all game entities."""
    
    _next_id: int = 1
    
    def __init__(self, game: Optional[Game] = None):
        self.entity_id: int = Entity._next_id
        Entity._next_id += 1
        self.game: Optional[Game] = game
        self.zone: Zone = Zone.INVALID
        self.tags: Dict[int, int] = {}
    
    @classmethod
    def reset_ids(cls) -> None:
        """Reset entity ID counter for new game."""
        cls._next_id = 1
    
    def get_tag(self, tag: GameTag, default: int = 0) -> int:
        """Get a tag value."""
        return self.tags.get(tag.value, default)
    
    def set_tag(self, tag: GameTag, value: int) -> None:
        """Set a tag value."""
        self.tags[tag.value] = value
    
    def has_tag(self, tag: GameTag) -> bool:
        """Check if tag is set and non-zero."""
        return self.tags.get(tag.value, 0) != 0


class Card(Entity):
    """A card in the game."""
    
    def __init__(self, data: CardData, game: Optional[Game] = None):
        super().__init__(game)
        self.data: CardData = data
        self.controller: Optional[Player] = None
        self.zone_position: int = 0
        
        # Dynamic stats (can be modified)
        self._cost: int = data.cost
        self._attack: int = data.attack
        self._health: int = data.health
        self._max_health: int = data.health
        self._armor: int = data.armor
        self._durability: int = data.durability
        self._damage: int = 0
        
        # State flags
        self.exhausted: bool = False
        self.attacks_this_turn: int = 0
        self.frozen: bool = False
        self.silenced: bool = False
        self.immune: bool = False
        self.cant_attack: bool = False
        self.cant_be_targeted: bool = False
        
        # Keyword states (can be silenced)
        self._taunt: bool = data.taunt
        self._divine_shield: bool = data.divine_shield
        self._charge: bool = data.charge
        self._windfury: bool = data.windfury
        self._stealth: bool = data.stealth
        self._poisonous: bool = data.poisonous
        self._lifesteal: bool = data.lifesteal
        self._rush: bool = data.rush
        self._reborn: bool = data.reborn
    
    def clone(self) -> 'Card':
        """Create a deep copy of the card."""
        # Create new instance of same class (Minion, Spell, etc.)
        new_card = type(self)(self.data, None)
        
        # Copy dynamic stats
        new_card._cost = self._cost
        new_card._attack = self._attack
        new_card._health = self._health
        new_card._max_health = self._max_health
        new_card._armor = self._armor
        new_card._durability = self._durability
        new_card._damage = self._damage
        
        # Copy states
        new_card.zone = self.zone
        new_card.zone_position = self.zone_position
        new_card.exhausted = self.exhausted
        new_card.attacks_this_turn = self.attacks_this_turn
        new_card.frozen = self.frozen
        new_card.silenced = self.silenced
        new_card.immune = self.immune
        new_card.cant_attack = self.cant_attack
        new_card.cant_be_targeted = self.cant_be_targeted
        
        # Copy keywords
        new_card._taunt = self._taunt
        new_card._divine_shield = self._divine_shield
        new_card._charge = self._charge
        new_card._windfury = self._windfury
        new_card._stealth = self._stealth
        new_card._poisonous = self._poisonous
        new_card._lifesteal = self._lifesteal
        new_card._rush = self._rush
        new_card._reborn = self._reborn
        
        # Copy tags
        new_card.tags = self.tags.copy()
        
        return new_card
    
    @property
    def card_id(self) -> str:
        return self.data.card_id
    
    @property
    def name(self) -> str:
        return self.data.name
    
    @property
    def card_type(self) -> CardType:
        return self.data.card_type
    
    @property
    def cost(self) -> int:
        return max(0, self._cost)
    
    @cost.setter
    def cost(self, value: int) -> None:
        self._cost = value
    
    @property
    def attack(self) -> int:
        return max(0, self._attack)
    
    @attack.setter
    def attack(self, value: int) -> None:
        self._attack = value
    
    @property
    def health(self) -> int:
        return self._max_health - self._damage
    
    @health.setter
    def health(self, value: int) -> None:
        self._max_health = value
        self._damage = max(0, self._max_health - value)
    
    @property
    def max_health(self) -> int:
        return self._max_health
    
    @max_health.setter
    def max_health(self, value: int) -> None:
        self._max_health = value
    
    @property
    def damage(self) -> int:
        return self._damage
    
    @damage.setter
    def damage(self, value: int) -> None:
        self._damage = max(0, value)
    
    # Keyword properties (affected by silence)
    @property
    def taunt(self) -> bool:
        return self._taunt and not self.silenced
    
    @taunt.setter
    def taunt(self, value: bool) -> None:
        self._taunt = value
    
    @property
    def divine_shield(self) -> bool:
        return self._divine_shield and not self.silenced
    
    @divine_shield.setter
    def divine_shield(self, value: bool) -> None:
        self._divine_shield = value
    
    @property
    def charge(self) -> bool:
        return self._charge and not self.silenced
    
    @charge.setter
    def charge(self, value: bool) -> None:
        self._charge = value
    
    @property
    def windfury(self) -> bool:
        return self._windfury and not self.silenced
    
    @windfury.setter
    def windfury(self, value: bool) -> None:
        self._windfury = value
    
    @property
    def stealth(self) -> bool:
        return self._stealth and not self.silenced
    
    @stealth.setter
    def stealth(self, value: bool) -> None:
        self._stealth = value
    
    @property
    def poisonous(self) -> bool:
        return self._poisonous and not self.silenced
    
    @poisonous.setter
    def poisonous(self, value: bool) -> None:
        self._poisonous = value
    
    @property
    def lifesteal(self) -> bool:
        return self._lifesteal and not self.silenced
    
    @lifesteal.setter
    def lifesteal(self, value: bool) -> None:
        self._lifesteal = value
    
    @property
    def rush(self) -> bool:
        return self._rush and not self.silenced
    
    @rush.setter
    def rush(self, value: bool) -> None:
        self._rush = value
    
    @property
    def reborn(self) -> bool:
        return self._reborn and not self.silenced

    @reborn.setter
    def reborn(self, value: bool) -> None:
        self._reborn = value
    
    def can_attack(self) -> bool:
        """Check if this entity can attack."""
        if self.cant_attack or self.frozen:
            return False
        if self.exhausted and not self.charge and not self.rush:
            return False
        max_attacks = 2 if self.windfury else 1
        if self.attacks_this_turn >= max_attacks:
            return False
        return self.attack > 0
    
    def is_dead(self) -> bool:
        """Check if the entity should be removed from play."""
        return self.health <= 0 or self.zone == Zone.GRAVEYARD
    
    def silence(self) -> None:
        """Silence this entity, removing all card text."""
        self.silenced = True
        self._taunt = False
        self._divine_shield = False
        self._windfury = False
        self._stealth = False
        self._poisonous = False
        self._lifesteal = False
        # Restore health to base
        self._max_health = self.data.health
        self._attack = self.data.attack
    
    def destroy(self) -> None:
        """Destroy this entity."""
        if self.game:
            self.game.destroy(self)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.name}' [{self.card_id}] {self.attack}/{self.health}>"


class Minion(Card):
    """A minion card."""
    
    def __init__(self, data: CardData, game: Optional[Game] = None):
        super().__init__(data, game)
    
    @property
    def race(self) -> Race:
        return self.data.race


class Spell(Card):
    """A spell card."""
    
    def __init__(self, data: CardData, game: Optional[Game] = None):
        super().__init__(data, game)
    
    @property
    def spell_school(self) -> SpellSchool:
        return self.data.spell_school


class Weapon(Card):
    """A weapon card."""
    
    def __init__(self, data: CardData, game: Optional[Game] = None):
        super().__init__(data, game)
        self._durability = data.durability
        self._max_durability = data.durability
    
    @property
    def durability(self) -> int:
        return self._durability
    
    @durability.setter
    def durability(self, value: int) -> None:
        self._durability = value
    
    def lose_durability(self, amount: int = 1) -> None:
        """Weapon loses durability (usually on attack)."""
        self._durability -= amount
        if self._durability <= 0:
            self.destroy()


class Hero(Card):
    """A hero card."""
    
    def __init__(self, data: CardData, game: Optional[Game] = None):
        super().__init__(data, game)
        self.weapon: Optional[Weapon] = None
        self.hero_power: Optional[HeroPower] = None
    
    @property
    def armor(self) -> int:
        return self._armor
    
    @armor.setter
    def armor(self, value: int) -> None:
        self._armor = max(0, value)
    
    def take_damage(self, amount: int) -> int:
        """Hero takes damage, armor absorbs first."""
        if self.immune:
            return 0
        
        armor_absorbed = min(self._armor, amount)
        self._armor -= armor_absorbed
        remaining = amount - armor_absorbed
        
        if remaining > 0:
            self._damage += remaining
        
        return amount
    
    def gain_armor(self, amount: int) -> None:
        """Hero gains armor."""
        self._armor += amount


class HeroPower(Card):
    """A hero power."""
    
    def __init__(self, data: CardData, game: Optional[Game] = None):
        super().__init__(data, game)
        self.used_this_turn: bool = False
    
    def can_use(self) -> bool:
        """Check if hero power can be used."""
        if self.used_this_turn:
            return False
        if self.controller and self.controller.mana < self.cost:
            return False
        return True
    
    def reset_for_turn(self) -> None:
        """Reset hero power for new turn."""
        self.used_this_turn = False


class Location(Card):
    """A location card."""
    
    def __init__(self, data: CardData, game: Optional[Game] = None):
        super().__init__(data, game)
        self.cooldown: int = 0
        # Durability from card data, default 3
        self._durability: int = data.durability if hasattr(data, 'durability') and data.durability else 3
    
    @property
    def durability(self) -> int:
        return self._durability
    
    def can_use(self) -> bool:
        """Check if location can be used."""
        return self.cooldown == 0 and self._durability > 0

    
    def use(self) -> None:
        """Use the location's ability."""
        self.cooldown = 1
        self._durability -= 1
        if self._durability <= 0:
            self.destroy()
    
    def reduce_cooldown(self) -> None:
        """Reduce cooldown at start of turn."""
        if self.cooldown > 0:
            self.cooldown -= 1
