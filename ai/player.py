"""Player state representation for HearthstoneOne AI."""

from dataclasses import dataclass, field
from typing import List, Optional
from .card import CardInstance, CardClass


@dataclass
class HeroState:
    """
    State of a player's hero.
    
    Attributes:
        health: Current health points
        max_health: Maximum health (usually 30)
        armor: Current armor points
        attack: Current attack (from weapons/hero power)
        hero_class: The hero's class
        is_immune: Whether hero is immune to damage
        can_attack: Whether hero can attack this turn
    """
    health: int
    max_health: int = 30
    armor: int = 0
    attack: int = 0
    hero_class: CardClass = CardClass.NEUTRAL
    is_immune: bool = False
    can_attack: bool = False
    
    @property
    def effective_health(self) -> int:
        """Total health including armor."""
        return self.health + self.armor
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "health": self.health,
            "max_health": self.max_health,
            "armor": self.armor,
            "attack": self.attack,
            "hero_class": self.hero_class.name,
            "is_immune": self.is_immune,
            "can_attack": self.can_attack,
        }


@dataclass
class WeaponState:
    """
    State of a player's equipped weapon.
    
    Attributes:
        card_id: The weapon card ID
        name: Weapon name
        attack: Weapon attack value
        durability: Remaining durability
    """
    card_id: str
    name: str
    attack: int
    durability: int
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "card_id": self.card_id,
            "name": self.name,
            "attack": self.attack,
            "durability": self.durability,
        }


@dataclass
class HeroPowerState:
    """
    State of a player's hero power.
    
    Attributes:
        card_id: Hero power card ID
        name: Hero power name  
        cost: Current mana cost
        is_usable: Whether it can be used this turn
        times_used: Times used this turn
    """
    card_id: str
    name: str
    cost: int
    is_usable: bool
    times_used: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "card_id": self.card_id,
            "name": self.name,
            "cost": self.cost,
            "is_usable": self.is_usable,
            "times_used": self.times_used,
        }


@dataclass
class PlayerState:
    """
    Complete state of a player in the game.
    
    Attributes:
        player_id: Player identifier (1 or 2)
        hero: Hero state
        mana: Current available mana
        max_mana: Maximum mana crystals
        overload: Locked mana crystals
        overload_next: Overload for next turn
        hand: Cards in hand
        board: Minions on the battlefield
        deck_size: Number of cards remaining in deck
        fatigue: Current fatigue damage
        weapon: Equipped weapon (if any)
        hero_power: Hero power state
        secrets: Active secrets (hidden from opponent)
    """
    player_id: int
    hero: HeroState
    mana: int
    max_mana: int
    overload: int = 0
    overload_next: int = 0
    hand: List[CardInstance] = field(default_factory=list)
    board: List[CardInstance] = field(default_factory=list)
    deck_size: int = 0
    fatigue: int = 0
    weapon: Optional[WeaponState] = None
    hero_power: Optional[HeroPowerState] = None
    secrets: List[str] = field(default_factory=list)
    
    @classmethod
    def from_simulator_player(cls, sim_player, player_id: int) -> "PlayerState":
        """Create a PlayerState from a Simulator player object."""
        # Hero state
        hero = HeroState(
            health=sim_player.hero.health if sim_player.hero else 0,
            max_health=sim_player.hero.max_health if sim_player.hero else 30,
            armor=sim_player.hero.armor if sim_player.hero else 0,
            attack=sim_player.hero.attack if sim_player.hero else 0,
            is_immune=sim_player.hero.immune if sim_player.hero else False,
            can_attack=sim_player.hero.can_attack() if sim_player.hero else False,
        )
        
        # Hand cards
        hand = [CardInstance.from_simulator_card(c) for c in sim_player.hand]
        
        # Board minions
        board = [CardInstance.from_simulator_card(c) for c in sim_player.board]
        
        # Weapon
        weapon = None
        if sim_player.weapon:
            weapon = WeaponState(
                card_id=sim_player.weapon.card_id,
                name=sim_player.weapon.name,
                attack=sim_player.weapon.attack,
                durability=sim_player.weapon.durability,
            )
            
        # Hero power
        hero_power = None
        if sim_player.hero_power:
            hp = sim_player.hero_power
            hero_power = HeroPowerState(
                card_id=hp.card_id,
                name=hp.name,
                cost=hp.cost,
                is_usable=hp.can_use(),
                times_used=1 if hp.used_this_turn else 0,
            )
            
        return cls(
            player_id=player_id,
            hero=hero,
            mana=sim_player.mana,
            max_mana=sim_player.mana_crystals,
            overload=sim_player.overload,
            overload_next=sim_player.overload_next_turn,
            hand=hand,
            board=board,
            deck_size=len(sim_player.deck),
            fatigue=sim_player.fatigue_counter,
            weapon=weapon,
            hero_power=hero_power,
            secrets=[s.card_id for s in sim_player.secrets]
        )

    @classmethod
    def from_fireplace_player(cls, fp_player, player_id: int) -> "PlayerState":
        """
        Create a PlayerState from a Fireplace player object.
        
        Args:
            fp_player: Fireplace Player entity
            player_id: Player identifier (1 or 2)
            
        Returns:
            PlayerState representing the player's current state
        """
        # Hero state
        hero = HeroState(
            health=fp_player.hero.health,
            max_health=fp_player.hero.max_health,
            armor=fp_player.hero.armor,
            attack=getattr(fp_player.hero, 'atk', 0),
            is_immune=getattr(fp_player.hero, 'immune', False),
            can_attack=getattr(fp_player.hero, 'can_attack', False),
        )
        
        # Hand cards
        hand = []
        for i, card in enumerate(fp_player.hand):
            instance = CardInstance.from_fireplace_card(card)
            instance.zone_position = i
            hand.append(instance)
        
        # Board minions
        board = []
        for i, card in enumerate(fp_player.field):
            instance = CardInstance.from_fireplace_card(card)
            instance.zone_position = i
            board.append(instance)
        
        # Weapon
        weapon = None
        if fp_player.weapon:
            weapon = WeaponState(
                card_id=fp_player.weapon.id,
                name=getattr(fp_player.weapon, 'name', fp_player.weapon.id),
                attack=fp_player.weapon.atk,
                durability=fp_player.weapon.durability,
            )
        
        # Hero power
        hero_power = None
        if fp_player.hero.power:
            hp = fp_player.hero.power
            hero_power = HeroPowerState(
                card_id=hp.id,
                name=getattr(hp, 'name', hp.id),
                cost=hp.cost,
                is_usable=hp.is_usable(),
                times_used=getattr(hp, 'times_used', 0),
            )
        
        # Secrets
        secrets = [s.id for s in fp_player.secrets]
        
        return cls(
            player_id=player_id,
            hero=hero,
            mana=fp_player.mana,
            max_mana=fp_player.max_mana,
            overload=getattr(fp_player, 'overload', 0),
            overload_next=getattr(fp_player, 'overload_owed', 0),
            hand=hand,
            board=board,
            deck_size=len(fp_player.deck),
            fatigue=getattr(fp_player, 'fatigue_counter', 0),
            weapon=weapon,
            hero_power=hero_power,
            secrets=secrets,
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "player_id": self.player_id,
            "hero": self.hero.to_dict(),
            "mana": self.mana,
            "max_mana": self.max_mana,
            "overload": self.overload,
            "overload_next": self.overload_next,
            "hand": [c.to_dict() for c in self.hand],
            "hand_size": len(self.hand),
            "board": [c.to_dict() for c in self.board],
            "board_size": len(self.board),
            "deck_size": self.deck_size,
            "fatigue": self.fatigue,
            "weapon": self.weapon.to_dict() if self.weapon else None,
            "hero_power": self.hero_power.to_dict() if self.hero_power else None,
            "secrets_count": len(self.secrets),
        }
