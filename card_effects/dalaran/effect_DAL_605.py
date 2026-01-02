"""Effect for DAL_605 in DALARAN"""

def on_play(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 1, source)