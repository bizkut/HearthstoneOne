"""Effect for DAL_078 in DALARAN"""

def battlecry(game, source, target):
    if target: game.heal(target, 3)