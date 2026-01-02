"""Effect for CORE_CS2_235 in CORE"""

def on_play(game, source, target):
    if target: source.controller.draw(1); target.health += 2