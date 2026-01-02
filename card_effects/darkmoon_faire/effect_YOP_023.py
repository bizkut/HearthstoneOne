"""Effect for YOP_023 in DARKMOON_FAIRE"""

def on_play(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 1, source)