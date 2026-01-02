"""Effect for MIS_708 in WHIZBANGS_WORKSHOP"""


def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    others = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_class != source.controller.hero.data.card_class]
    if others:
        for _ in range(5):
             source.controller.add_to_hand(create_card(random.choice(others), game))
