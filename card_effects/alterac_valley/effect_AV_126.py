"""Effect for AV_126 in ALTERAC_VALLEY"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 1, source)