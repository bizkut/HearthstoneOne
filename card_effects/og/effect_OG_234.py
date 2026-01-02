"""Effect for OG_234 in OG"""

def battlecry(game, source, target):
    if target: game.heal(target, 5)