"""Effect for CORE_SCH_158 in CORE"""
from simulator.enums import Race

def on_play(game, source, target):
    player = source.controller
    from simulator.card_loader import CardDatabase
    demons = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.DEMON]
    import random
    options = random.sample(demons, 3)
    def on_choose(game, card_id):
        c = create_card(card_id, game)
        c.cost -= 1
        game.current_player.add_to_hand(c)
    game.initiate_discover(player, options, on_choose)