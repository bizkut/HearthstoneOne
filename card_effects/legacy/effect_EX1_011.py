"""Effect for EX1_011 in LEGACY"""

def battlecry(game, source, target):
    if target: game.heal(target, 2)