"""Hearthstone Simulator Package.

A Python-based Hearthstone game engine with support for all cards.
"""

from .enums import (
    GamePhase, Step, Zone, CardType, CardClass, 
    Rarity, Race, SpellSchool, PlayState, Mulligan, GameTag
)
from .entities import (
    Entity, CardData, Card, Minion, Spell, Weapon, Hero, HeroPower, Location
)
from .player import Player
from .game import Game, GameConfig
from .card_loader import CardDatabase, create_card, create_deck


__all__ = [
    # Enums
    'GamePhase', 'Step', 'Zone', 'CardType', 'CardClass',
    'Rarity', 'Race', 'SpellSchool', 'PlayState', 'Mulligan', 'GameTag',
    # Entities
    'Entity', 'CardData', 'Card', 'Minion', 'Spell', 'Weapon', 'Hero', 'HeroPower', 'Location',
    # Core
    'Player', 'Game', 'GameConfig',
    # Card loading
    'CardDatabase', 'create_card', 'create_deck',
]


__version__ = '0.1.0'
