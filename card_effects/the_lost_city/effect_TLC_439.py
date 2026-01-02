"""Effect for TLC_439 in THE_LOST_CITY"""

def on_play(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 2, source)