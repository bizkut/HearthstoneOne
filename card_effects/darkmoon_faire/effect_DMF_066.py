"""Effect for DMF_066 in DARKMOON_FAIRE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 4, source)