"""Effect for CS2_235 in LEGACY"""

def on_play(game, source, target):
    if target: source.controller.draw(1); target.health += 2