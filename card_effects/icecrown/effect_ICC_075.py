"""Effect for ICC_075 in ICECROWN"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 1, source)