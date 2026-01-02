"""Effect for AT_111 in TGT"""

def battlecry(game, source, target):
    if target: game.heal(target, 4)