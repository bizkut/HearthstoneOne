"""Effect for BAR_745 in THE_BARRENS"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)