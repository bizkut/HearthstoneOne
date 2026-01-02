"""Effect for BAR_316 in THE_BARRENS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)