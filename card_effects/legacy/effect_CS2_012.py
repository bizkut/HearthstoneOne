"""Effect for CS2_012 in LEGACY"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)
    source.controller.draw(1)