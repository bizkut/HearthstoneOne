"""Effect for FIR_778 in EMERALD_DREAM"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 9, source)