"""Effect for CORE_UNG_941 in CORE"""
from simulator.enums import CardType
from simulator.card_loader import CardDatabase, create_card
import random

def on_play(game, source, target):
    player = source.controller
    spells = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.SPELL]
    options = random.sample(spells, min(3, len(spells)))
    def on_choose(game, card_id):
        c = create_card(card_id, game)
        if c:
            c._cost = max(0, c.cost - 2)
            game.current_player.add_to_hand(c)
    game.initiate_discover(player, options, on_choose)