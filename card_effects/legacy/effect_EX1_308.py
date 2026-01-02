"""Effect for EX1_308 in LEGACY"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 4, source); source.controller.discard(1)