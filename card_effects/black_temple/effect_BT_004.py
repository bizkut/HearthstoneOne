"""Effect for BT_004 in BLACK_TEMPLE"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 2, source)