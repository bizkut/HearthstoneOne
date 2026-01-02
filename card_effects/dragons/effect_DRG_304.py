"""Effect for DRG_304 in DRAGONS"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 3, source)