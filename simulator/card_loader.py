"""Hearthstone Simulator - Card Loader.

Loads card data from hearthstone_data package.
"""

from __future__ import annotations

from typing import Dict, Optional, List
from hearthstone import cardxml
from hearthstone.enums import CardType as HSCardType, Race as HSRace, Rarity as HSRarity

from .enums import CardType, CardClass, Rarity, Race, SpellSchool, GameTag
from .entities import CardData, Card, Minion, Spell, Weapon, Hero, HeroPower, Location
from card_generator.cache import EffectCache


class CardDatabase:
    """Database of all cards loaded from hearthstone_data."""
    
    _instance: Optional[CardDatabase] = None
    _cards: Dict[str, CardData] = {}
    _loaded: bool = False
    _cache: EffectCache = EffectCache()
    
    def __new__(cls) -> CardDatabase:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> CardDatabase:
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def load(cls) -> Dict[str, CardData]:
        """Load all cards from hearthstone_data."""
        if cls._loaded:
            return cls._cards
        
        db, _ = cardxml.load()
        
        for card_id, card in db.items():
            try:
                card_data = cls._convert_card(card)
                if card_data:
                    cls._cards[card_id] = card_data
            except Exception as e:
                print(f"Error loading card {card_id}: {e}")
                pass
        
        cls._loaded = True
        return cls._cards
    
    @classmethod
    def _convert_card(cls, card) -> Optional[CardData]:
        """Convert a hearthstone_data card to CardData."""
        # Get card type
        card_type = cls._map_card_type(getattr(card, 'type', None))
        if card_type == CardType.INVALID:
            return None
        
        # Get basic properties
        card_id = getattr(card, 'id', '') or ''
        name = getattr(card, 'name', '') or ''
        text = getattr(card, 'description', '') or ''
        
        # Get set
        try:
            from hearthstone.enums import CardSet
            card_set = CardSet(getattr(card, 'card_set', 0)).name
        except (ValueError, AttributeError, ImportError):
            card_set = "UNKNOWN"
            
        cost = getattr(card, 'cost', 0) or 0
        attack = getattr(card, 'atk', 0) or 0
        health = getattr(card, 'health', 0) or 0
        
        # Get class
        card_class = cls._map_card_class(getattr(card, 'card_class', None))
        
        # Get rarity
        rarity = cls._map_rarity(getattr(card, 'rarity', None))
        
        # Get race (for minions)
        race = cls._map_race(getattr(card, 'race', None))
        
        # Get spell school
        spell_school = cls._map_spell_school(getattr(card, 'spell_school', None))
        
        # Get keywords
        mechanics = getattr(card, 'mechanics', []) or []
        
        collectible = getattr(card, 'collectible', False)
        
        return CardData(
            card_id=card_id,
            name=name,
            text=text,
            card_set=card_set,
            cost=cost,
            attack=attack,
            health=health,
            durability=getattr(card, 'durability', 0) or 0,
            card_type=card_type,
            card_class=card_class,
            rarity=rarity,
            race=race,
            spell_school=spell_school,
            collectible=collectible,
            taunt='TAUNT' in mechanics,
            divine_shield='DIVINE_SHIELD' in mechanics,
            charge='CHARGE' in mechanics,
            windfury='WINDFURY' in mechanics,
            stealth='STEALTH' in mechanics,
            poisonous='POISONOUS' in mechanics,
            lifesteal='LIFESTEAL' in mechanics,
            rush='RUSH' in mechanics,
            reborn='REBORN' in mechanics,
            battlecry='BATTLECRY' in mechanics or 'Battlecry:' in text,
            deathrattle='DEATHRATTLE' in mechanics or 'Deathrattle:' in text,
            secret='SECRET' in mechanics,
            discover='DISCOVER' in mechanics,
            outcast='OUTCAST' in mechanics,
            tags={GameTag.SPELLPOWER.value: getattr(card, 'spell_damage', 0) or 0}
        )
    
    @classmethod
    def _map_card_type(cls, hs_type) -> CardType:
        """Map hearthstone enum to our CardType."""
        if hs_type is None:
            return CardType.INVALID
        
        mapping = {
            HSCardType.MINION: CardType.MINION,
            HSCardType.SPELL: CardType.SPELL,
            HSCardType.WEAPON: CardType.WEAPON,
            HSCardType.HERO: CardType.HERO,
            HSCardType.HERO_POWER: CardType.HERO_POWER,
        }
        
        # Handle Location type (may not be in older hearthstone library)
        if hasattr(HSCardType, 'LOCATION'):
            mapping[HSCardType.LOCATION] = CardType.LOCATION
        
        return mapping.get(hs_type, CardType.INVALID)
    
    @classmethod
    def _map_card_class(cls, hs_class) -> CardClass:
        """Map hearthstone enum to our CardClass."""
        if hs_class is None:
            return CardClass.NEUTRAL
        
        try:
            return CardClass(hs_class.value)
        except (ValueError, AttributeError):
            return CardClass.NEUTRAL
    
    @classmethod
    def _map_rarity(cls, hs_rarity) -> Rarity:
        """Map hearthstone enum to our Rarity."""
        if hs_rarity is None:
            return Rarity.FREE
        
        try:
            return Rarity(hs_rarity.value)
        except (ValueError, AttributeError):
            return Rarity.FREE
    
    @classmethod
    def _map_race(cls, hs_race) -> Race:
        """Map hearthstone enum to our Race."""
        if hs_race is None:
            return Race.INVALID
        
        try:
            return Race(hs_race.value)
        except (ValueError, AttributeError):
            return Race.INVALID
    
    @classmethod
    def _map_spell_school(cls, hs_spell_school) -> SpellSchool:
        """Map hearthstone enum to our SpellSchool."""
        if hs_spell_school is None:
            return SpellSchool.NONE
        
        try:
            return SpellSchool(hs_spell_school.value)
        except (ValueError, AttributeError):
            return SpellSchool.NONE
    
    @classmethod
    def get_card(cls, card_id: str) -> Optional[CardData]:
        """Get card data by ID."""
        if not cls._loaded:
            cls.load()
        return cls._cards.get(card_id)
    
    @classmethod
    def get_collectible_cards(cls) -> List[CardData]:
        """Get all collectible cards."""
        if not cls._loaded:
            cls.load()
        return [c for c in cls._cards.values() if c.collectible]
    
    @classmethod
    def get_cards_by_class(cls, card_class: CardClass) -> List[CardData]:
        """Get all cards for a specific class."""
        if not cls._loaded:
            cls.load()
        return [c for c in cls._cards.values() 
                if c.card_class == card_class or c.card_class == CardClass.NEUTRAL]
    
    @classmethod
    def search(cls, query: str) -> List[CardData]:
        """Search cards by name or text."""
        if not cls._loaded:
            cls.load()
        query = query.lower()
        return [c for c in cls._cards.values() 
                if query in c.name.lower() or query in c.text.lower()]
    
    @classmethod
    def count(cls) -> int:
        """Get total number of cards."""
        if not cls._loaded:
            cls.load()
        return len(cls._cards)


def create_card(card_id: str, game=None) -> Optional[Card]:
    """Create a card instance from card ID."""
    data = CardDatabase.get_card(card_id)
    if not data:
        return None
    
    if data.card_type == CardType.MINION:
        card = Minion(data, game)
    elif data.card_type == CardType.SPELL:
        card = Spell(data, game)
    elif data.card_type == CardType.WEAPON:
        card = Weapon(data, game)
    elif data.card_type == CardType.HERO:
        card = Hero(data, game)
    elif data.card_type == CardType.HERO_POWER:
        card = HeroPower(data, game)
        # Load hero power effect handler
        if game:
            from card_effects.hero_powers import get_hero_power_handler
            handler = get_hero_power_handler(card_id)
            if handler:
                game._battlecry_handlers[card_id] = handler
    elif data.card_type == CardType.LOCATION:
        card = Location(data, game)
    else:
        card = Card(data, game)

    # Load effects if game is provided
    if game:
        effects = CardDatabase._cache.load_effect(card_id, data.card_set)
        if effects:
            if "battlecry" in effects:
                game._battlecry_handlers[card_id] = effects["battlecry"]
            if "deathrattle" in effects:
                game._deathrattle_handlers[card_id] = effects["deathrattle"]
            if "on_play" in effects:
                # Spells use on_play for their logic
                game._battlecry_handlers[card_id] = effects["on_play"]
            if "setup" in effects:
                # Setup is called immediately to register triggers
                effects["setup"](game, card)
            if "get_valid_targets" in effects:
                game._target_handlers[card_id] = effects["get_valid_targets"]
                
    return card


def create_deck(card_ids: List[str], game=None) -> List[Card]:
    """Create a deck from a list of card IDs."""
    deck = []
    for card_id in card_ids:
        card = create_card(card_id, game)
        if card:
            deck.append(card)
    return deck
