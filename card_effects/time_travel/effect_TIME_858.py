"""Effect for TIME_858 in TIME_TRAVEL"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 5, source)