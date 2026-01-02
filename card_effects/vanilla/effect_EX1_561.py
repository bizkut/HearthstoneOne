"""Effect for EX1_561 in VANILLA"""


def battlecry(game, source, target):
    # Alexstrasza
    if target: target.health = 15
