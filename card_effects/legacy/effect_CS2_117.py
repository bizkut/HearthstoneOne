"""Effect for CS2_117 in LEGACY"""

def battlecry(game, source, target):
    if target: game.heal(target, 3)