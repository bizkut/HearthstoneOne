"""Effect for VAN_DS1_055 in VANILLA"""

def battlecry(game, source, target):
    if target: game.heal(target, 2)