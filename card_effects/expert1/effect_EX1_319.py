"""Effect for EX1_319 in EXPERT1"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)