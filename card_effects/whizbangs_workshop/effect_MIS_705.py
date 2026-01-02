"""Effect for MIS_705 in WHIZBANGS_WORKSHOP"""


def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    taunts = [c.card_id for c in CardDatabase.get_collectible_cards() if c.taunt]
    if taunts:
        for _ in range(5):
             source.controller.add_to_hand(create_card(random.choice(taunts), game))
