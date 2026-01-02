"""Effect for TIME_004 in TIME_TRAVEL"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 7, source)