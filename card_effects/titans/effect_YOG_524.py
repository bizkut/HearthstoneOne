"""Effect for YOG_524 in TITANS"""


def battlecry(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    cards = [c.card_id for c in CardDatabase.get_collectible_cards() if 'Overload' in (c.text or "")]
    if cards:
        source.controller.add_to_hand(create_card(random.choice(cards), game))
