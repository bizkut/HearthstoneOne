"""Effect for CS2_088 in LEGACY"""

def battlecry(game, source, target):
    if target: game.heal(target, 6)