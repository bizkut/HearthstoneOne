"""Effect for CS2_022 in LEGACY"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 1, source)
    source.controller.draw(1)