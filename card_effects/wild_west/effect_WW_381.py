"""Effect for WW_381 in WILD_WEST"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 4, source)