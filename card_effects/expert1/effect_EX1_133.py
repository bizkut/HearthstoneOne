"""Effect for EX1_133 in EXPERT1"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)