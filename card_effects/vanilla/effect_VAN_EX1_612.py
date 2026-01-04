"""Effect for VAN_EX1_612 in VANILLA"""

def on_play(game, source, target):
    source.controller.draw(1); source.controller.gain_armor(8)