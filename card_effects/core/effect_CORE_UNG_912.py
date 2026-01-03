"""Effect for CORE_UNG_912 in CORE"""
from simulator.enums import Race

def battlecry(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    options = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.BEAST]
    if options:
        source.controller.add_to_hand(create_card(random.choice(options), game))