"""Hearthstone Simulator - Enumerations and Types.

Core type definitions for the simulator.
"""

from enum import Enum, IntEnum, auto
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .entities import Entity


class GamePhase(Enum):
    """Game phases."""
    INVALID = auto()
    DECK_BUILDING = auto()
    MULLIGAN = auto()
    MAIN_ACTION = auto()
    MAIN_COMBAT = auto()
    MAIN_END = auto()
    GAME_OVER = auto()


class Step(Enum):
    """Turn steps."""
    INVALID = auto()
    BEGIN_MULLIGAN = auto()
    MAIN_BEGIN = auto()
    MAIN_ACTION = auto()
    MAIN_COMBAT = auto()
    MAIN_END = auto()
    MAIN_NEXT = auto()
    FINAL_WRAPUP = auto()
    FINAL_GAMEOVER = auto()
    

class Zone(IntEnum):
    """Card zones."""
    INVALID = 0
    PLAY = 1
    DECK = 2
    HAND = 3
    GRAVEYARD = 4
    REMOVEDFROMGAME = 5
    SETASIDE = 6
    SECRET = 7


class CardType(IntEnum):
    """Card types."""
    INVALID = 0
    GAME = 1
    PLAYER = 2
    HERO = 3
    MINION = 4
    SPELL = 5
    ENCHANTMENT = 6
    WEAPON = 7
    ITEM = 8
    TOKEN = 9
    HERO_POWER = 10
    LOCATION = 11


class CardClass(IntEnum):
    """Card classes (hero classes)."""
    INVALID = 0
    DEATHKNIGHT = 1
    DRUID = 2
    HUNTER = 3
    MAGE = 4
    PALADIN = 5
    PRIEST = 6
    ROGUE = 7
    SHAMAN = 8
    WARLOCK = 9
    WARRIOR = 10
    DREAM = 11
    NEUTRAL = 12
    DEMONHUNTER = 14


class Rarity(IntEnum):
    """Card rarity."""
    INVALID = 0
    COMMON = 1
    FREE = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5


class Race(IntEnum):
    """Minion races/tribes."""
    INVALID = 0
    BLOODELF = 1
    DRAENEI = 2
    DWARF = 3
    GNOME = 4
    GOBLIN = 5
    HUMAN = 6
    NIGHTELF = 7
    ORC = 8
    TAUREN = 9
    TROLL = 10
    UNDEAD = 11
    WORGEN = 12
    GOBLIN2 = 13
    MURLOC = 14
    DEMON = 15
    SCOURGE = 16
    MECHANICAL = 17
    ELEMENTAL = 18
    OGRE = 19
    BEAST = 20
    TOTEM = 21
    NERUBIAN = 22
    PIRATE = 23
    DRAGON = 24
    ALL = 26
    NAGA = 92
    QUILBOAR = 93
    UNDEAD_NEW = 94


class SpellSchool(IntEnum):
    """Spell schools."""
    NONE = 0
    ARCANE = 1
    FIRE = 2
    FROST = 3
    NATURE = 4
    HOLY = 5
    SHADOW = 6
    FEL = 7


class PlayState(IntEnum):
    """Player play state."""
    INVALID = 0
    PLAYING = 1
    WINNING = 2
    LOSING = 3
    WON = 4
    LOST = 5
    TIED = 6
    DISCONNECTED = 7
    CONCEDED = 8


class Mulligan(IntEnum):
    """Mulligan state."""
    INVALID = 0
    INPUT = 1
    DEALING = 2
    WAITING = 3
    DONE = 4


class GameTag(IntEnum):
    """Common game tags (subset of full tags)."""
    INVALID = 0
    TAG_SCRIPT_DATA_NUM_1 = 2
    TAG_SCRIPT_DATA_NUM_2 = 3
    TAG_SCRIPT_DATA_ENT_1 = 4
    TAG_SCRIPT_DATA_ENT_2 = 5
    DAMAGE = 44
    HEALTH = 45
    ATK = 47
    COST = 48
    EXHAUSTED = 50
    CONTROLLER = 50
    ZONE = 49
    CARD_ID = 56
    CLASS = 199
    CARDRACE = 200
    FACTION = 201
    CARDTYPE = 202
    RARITY = 203
    ELITE = 114
    TAUNT = 190
    WINDFURY = 189
    DIVINE_SHIELD = 194
    CHARGE = 197
    STEALTH = 191
    POISONOUS = 363
    LIFESTEAL = 685
    RUSH = 791
    REBORN = 1543
    BATTLECRY = 218
    DEATHRATTLE = 217
    SPELL_SCHOOL = 1885
    ARMOR = 292
    FROZEN = 260
    CANT_ATTACK = 337
    CANT_BE_TARGETED = 360
    IMMUNE = 358
    SILENCED = 188
    SPELLPOWER = 106
    AURA = 362
    SECRET = 219
    DISCOVER = 415
    OUTCAST = 1118
