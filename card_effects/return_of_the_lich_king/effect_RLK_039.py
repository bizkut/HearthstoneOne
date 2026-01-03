"""Effect for RLK_039 in RETURN_OF_THE_LICH_KING"""
from simulator.enums import Race


def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    undeads = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.UNDEAD]
    while len(source.controller.board) < 7 and undeads:
        source.controller.summon(create_card(random.choice(undeads), game))
