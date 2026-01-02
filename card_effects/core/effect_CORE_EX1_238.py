"""Effect for CORE_EX1_238 in CORE"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 3, source); source.controller.overload += 1