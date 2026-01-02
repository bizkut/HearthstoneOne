"""Effect for EX1_238 in LEGACY"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 3, source); source.controller.overload += 1