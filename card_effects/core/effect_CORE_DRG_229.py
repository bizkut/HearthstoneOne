"""Effect for CORE_DRG_229 in CORE"""
from simulator.enums import Race

def battlecry(game, source, target):
    player = source.controller
    from simulator.card_loader import CardDatabase
    options = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.DRAGON]
    import random
    chosen = random.sample(options, min(3, len(options)))
    def on_choose(game, card_id):
        game.current_player.add_to_hand(create_card(card_id, game))
    game.initiate_discover(player, chosen, on_choose)