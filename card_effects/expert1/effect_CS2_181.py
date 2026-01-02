"""Effect for CS2_181 in EXPERT1"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 4, source)