"""Effect for VAN_EX1_129 in VANILLA"""

def on_play(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 1, source)