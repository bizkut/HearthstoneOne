"""Effect for NX2_002 in RETURN_OF_THE_LICH_KING"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 1, source)