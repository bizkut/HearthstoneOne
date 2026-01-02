"""Effect for DAL_544 in DALARAN"""

def battlecry(game, source, target):
    if target: game.heal(target, 2)