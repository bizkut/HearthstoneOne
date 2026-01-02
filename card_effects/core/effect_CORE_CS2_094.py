"""Effect for CORE_CS2_094 in CORE"""

def on_play(game, source, target):
    source.controller.draw(1)
    source.controller.hero.attack += 2