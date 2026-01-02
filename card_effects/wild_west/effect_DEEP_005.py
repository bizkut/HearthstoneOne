"""Effect for DEEP_005 in WILD_WEST"""


def deathrattle(game, source):
    from simulator.card_loader import CardDatabase
    import random
    options = [c.card_id for c in CardDatabase.get_collectible_cards() if c.cost <= 3 and 'Deathrattle:' in (c.text or "")]
    if options:
        for _ in range(2): source.controller.summon(create_card(random.choice(options), game))
