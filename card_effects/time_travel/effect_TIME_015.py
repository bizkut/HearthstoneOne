"""Effect for TIME_015 in TIME_TRAVEL"""

def battlecry(game, source, target):
    if target: game.heal(target, 3)