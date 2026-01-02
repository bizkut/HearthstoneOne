"""Effect for DMF_254 in DARKMOON_FAIRE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 30, source)