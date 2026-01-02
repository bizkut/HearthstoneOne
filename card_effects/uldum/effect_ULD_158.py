"""Effect for ULD_158 in ULDUM"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 1, source)