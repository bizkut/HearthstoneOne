"""Effect for VAN_CS2_045 in VANILLA"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source); source.controller.overload += 1