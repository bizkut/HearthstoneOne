from simulator.enums import CardType
"""Effect for TIME_861 in TIME_TRAVEL"""


def battlecry(game, source, target):
    # Get 3 random spells from the past
    from simulator.card_loader import CardDatabase
    import random
    options = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.SPELL and c.card_set != 'TIME_TRAVEL']
    for _ in range(3):
        source.controller.add_to_hand(create_card(random.choice(options), game))
