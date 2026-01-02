"""Effect for VAN_EX1_308 in VANILLA"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 4, source); source.controller.discard(1)