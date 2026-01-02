"""Effect for VAN_CS2_088 in VANILLA"""

def battlecry(game, source, target):
    if target: game.heal(target, 6)