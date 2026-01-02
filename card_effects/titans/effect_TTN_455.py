"""Effect for TTN_455 in TITANS"""

def battlecry(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 3, source)