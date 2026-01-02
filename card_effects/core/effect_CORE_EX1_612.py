"""Effect for CORE_EX1_612 in CORE"""

def on_play(game, source, target):
    source.controller.draw(1); source.controller.hero.gain_armor(8)