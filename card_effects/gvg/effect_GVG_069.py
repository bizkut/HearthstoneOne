"""Effect for GVG_069 in GVG"""

def battlecry(game, source, target):
    if target: game.heal(target, 8)