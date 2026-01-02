"""Effect for TOY_714 in WHIZBANGS_WORKSHOP"""

def on_play(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 1, source)