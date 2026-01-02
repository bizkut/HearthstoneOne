"""Effect for VAN_CS2_235 in VANILLA"""

def on_play(game, source, target):
    if target: source.controller.draw(1); target.health += 2