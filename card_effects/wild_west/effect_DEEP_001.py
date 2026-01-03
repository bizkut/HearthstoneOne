"""Effect for DEEP_001 in WILD_WEST"""
from simulator.enums import Race


def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    beasts = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.BEAST]
    undead = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.UNDEAD]
    if beasts and undead:
        b = create_card(random.choice(beasts), game)
        u = create_card(random.choice(undead), game)
        # Swap stats
        b.attack, u.attack = u.attack, b.attack
        b.health, u.health = u.health, b.health
        b.max_health, u.max_health = u.max_health, b.max_health
        source.controller.add_to_hand(b)
        source.controller.add_to_hand(u)
