"""Effect for VAN_CS2_022 in VANILLA"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 1, source)
    source.controller.draw(1)