"""Effect for TLC_633 in THE_LOST_CITY"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 6, source)