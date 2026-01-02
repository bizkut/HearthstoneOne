"""Effect for OG_280 in OG"""


def battlecry(game, source, target):
    # C'Thun: Deal damage equal to attack
    for _ in range(source.attack):
        opp = game.get_opponent(source.controller).board + [game.get_opponent(source.controller).hero]
        import random
        game.deal_damage(random.choice(opp), 1, source)
