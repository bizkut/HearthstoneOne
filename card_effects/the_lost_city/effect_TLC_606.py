"""Effect for TLC_606 in THE_LOST_CITY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)