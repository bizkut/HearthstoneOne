"""Effect for TLC_600 in THE_LOST_CITY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 5, source)