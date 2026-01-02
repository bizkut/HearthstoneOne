"""Effect for CS2_094 in LEGACY"""

def on_play(game, source, target):
    source.controller.draw(1)
    source.controller.hero.attack += 2