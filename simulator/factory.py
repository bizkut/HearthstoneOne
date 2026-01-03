from typing import TYPE_CHECKING
from .card_loader import CardDatabase
from .entities import Minion, Spell, Weapon, Hero, HeroPower, Card, CardData, Location
from .enums import CardType, CardClass, Rarity

if TYPE_CHECKING:
    from .player import Player

def create_card(card_id: str, controller: 'Player') -> Card:
    """Creates a Card instance from an ID using the database."""
    db = CardDatabase.get_instance()
    # Check if loaded? accessing _loaded is protected in theory but python..
    if not db._loaded:
        try:
            db.load()
        except:
            pass # Load might fail if no XML, we handle missing data below
        
    data = db._cards.get(card_id)
    
    if not data:
         # Create dummy data for unknown cards (e.g. from logs with new IDs)
         data = CardData(
             card_id=card_id, 
             name="Unknown", 
             cost=0, 
             card_type=CardType.SPELL, 
             card_class=CardClass.NEUTRAL,
             rarity=Rarity.COMMON,
             text="",
             mechanics=[],
             requirements=[]
         )

    game = controller.game if controller else None
    entity = None

    if data.card_type == CardType.MINION:
        entity = Minion(data, game)
    elif data.card_type == CardType.SPELL:
        entity = Spell(data, game)
    elif data.card_type == CardType.WEAPON:
        entity = Weapon(data, game)
    elif data.card_type == CardType.HERO:
        entity = Hero(data, game)
    elif data.card_type == CardType.HERO_POWER:
        entity = HeroPower(data, game)
    elif data.card_type == CardType.LOCATION:
        entity = Location(data, game)
    else:
        entity = Card(data, game)
        
    entity.controller = controller
    return entity
