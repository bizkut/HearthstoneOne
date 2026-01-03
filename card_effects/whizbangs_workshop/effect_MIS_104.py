"""Effect for MIS_104 in WHIZBANGS_WORKSHOP"""
from simulator.enums import Race


def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    beasts = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.BEAST]
    if beasts:
        for _ in range(5):
             source.controller.add_to_hand(create_card(random.choice(beasts), game))
