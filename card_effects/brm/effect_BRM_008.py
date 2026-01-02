"""Effect for BRM_008 in BRM"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)