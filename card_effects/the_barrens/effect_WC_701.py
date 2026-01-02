"""Effect for WC_701 in THE_BARRENS"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 1, source)