"""Effect for EX1_277 in LEGACY"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 10, source)