"""Effect for EX1_583 in EXPERT1"""

def battlecry(game, source, target):
    if target: game.heal(target, 4)