"""Effect for CS2_117 in EXPERT1"""

def battlecry(game, source, target):
    if target: game.heal(target, 3)