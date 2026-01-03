"""Effect for DEEP_022 in WILD_WEST"""
from simulator.enums import Race


def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    pirates = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.PIRATE and c.card_class != source.controller.hero.data.card_class]
    elementals = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.ELEMENTAL and c.card_class != source.controller.hero.data.card_class]
    if pirates: source.controller.add_to_hand(create_card(random.choice(pirates), game))
    if elementals: source.controller.add_to_hand(create_card(random.choice(elementals), game))
