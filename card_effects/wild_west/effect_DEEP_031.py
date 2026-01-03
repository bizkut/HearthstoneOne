from simulator.enums import CardType
"""Effect for DEEP_031 in WILD_WEST"""


def on_play(game, source, target):
    if target: game.deal_damage(target, 6, source)
    from simulator.card_loader import CardDatabase
    import random
    options = [c.card_id for c in CardDatabase.get_collectible_cards() if c.cost == 6 and c.card_type == CardType.MINION]
    if options:
        source.controller.summon(create_card(random.choice(options), game))
    source.controller.deck = source.controller.deck[:-6]
