"""Effect for CORE_EX1_561 in CORE"""


def battlecry(game, source, target):
    # Alexstrasza
    if target: target.health = 15
