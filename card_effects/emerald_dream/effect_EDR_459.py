"""Effect for EDR_459 in EMERALD_DREAM"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 3, source)