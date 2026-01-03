"""Effect for ETC_535 in BATTLE_OF_THE_BANDS"""
from simulator.enums import Race


def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    for cost in [1, 2, 3]:
        options = [c.card_id for c in CardDatabase.get_collectible_cards() 
                   if c.race == Race.ELEMENTAL and c.cost == cost]
        if options:
            source.controller.add_to_hand(create_card(random.choice(options), game))
