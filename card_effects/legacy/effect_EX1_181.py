"""Effect for EX1_181 in LEGACY"""
from simulator.enums import Race

def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    options = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.DEMON]
    if options:
        source.controller.add_to_hand(create_card(random.choice(options), game))