"""Effect for TIME_101 in TIME_TRAVEL"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 2, source)