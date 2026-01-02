"""Effect for DMF_101 in DARKMOON_FAIRE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)