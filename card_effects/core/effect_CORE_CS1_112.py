"""Effect for CORE_CS1_112 in CORE"""

def on_play(game, source, target):
    for m in source.controller.opponent.board[:]: game.deal_damage(m, 2, source)