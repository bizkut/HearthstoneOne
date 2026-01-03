"""Effect for CORE_UNG_072 in CORE"""
from simulator.enums import CardType
from simulator.card_loader import CardDatabase, create_card
import random

def battlecry(game, source, target):
    player = source.controller
    taunts = [c.card_id for c in CardDatabase.get_collectible_cards() if getattr(c, 'taunt', False) and c.card_type == CardType.MINION]
    options = random.sample(taunts, min(3, len(taunts)))
    def on_choose(game, card_id):
        c = create_card(card_id, game)
        if c:
            game.current_player.add_to_hand(c)
    game.initiate_discover(player, options, on_choose)