"""Effect for TIME_038 in TIME_TRAVEL"""


def battlecry(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    legends = [c.card_id for c in CardDatabase.get_collectible_cards() if c.rarity == 4]
    for _ in range(2):
        source.controller.summon(create_card(random.choice(legends), game))
