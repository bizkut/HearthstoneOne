"""Effect for VAN_CS2_117 in VANILLA"""

def battlecry(game, source, target):
    if target: game.heal(target, 3)