"""Effect for BAR_069 in THE_BARRENS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 6, source)