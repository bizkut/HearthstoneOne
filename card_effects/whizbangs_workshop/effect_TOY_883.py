"""Effect for TOY_883 in WHIZBANGS_WORKSHOP"""

def on_play(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 3, source)