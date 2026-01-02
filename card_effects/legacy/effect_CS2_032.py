"""Effect for CS2_032 in LEGACY"""

def on_play(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 5, source)