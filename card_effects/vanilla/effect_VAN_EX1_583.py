"""Effect for VAN_EX1_583 in VANILLA"""

def battlecry(game, source, target):
    if target: game.heal(target, 4)