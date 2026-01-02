"""Effect for ULD_240 in ULDUM"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 2, source)