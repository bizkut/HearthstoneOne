"""Effect for TIME_446 in TIME_TRAVEL"""


def on_play(game, source, target):
    p = source.controller
    import random
    from simulator.card_loader import CardDatabase
    demons = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.DEMON and c.cost >= 5]
    if demons:
        # Simplified Discover: add random to hand
        p.add_to_hand(create_card(random.choice(demons), game))
    
    # Deck check
    has_minion = any(c.card_type == CardType.MINION for c in p.deck)
    if not has_minion:
        # Next demon costs 0 logic placeholder
        pass
