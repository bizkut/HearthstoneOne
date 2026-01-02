"""Effect for VAN_EX1_561 in VANILLA"""

def battlecry(game, source, target):
    if target: target.health = 15