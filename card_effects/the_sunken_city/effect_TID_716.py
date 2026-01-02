"""Effect for TID_716 in THE_SUNKEN_CITY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 5, source)