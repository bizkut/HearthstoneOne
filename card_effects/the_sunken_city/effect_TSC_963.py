"""Effect for TSC_963 in THE_SUNKEN_CITY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)