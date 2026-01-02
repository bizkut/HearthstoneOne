"""Effect for EX1_124 in LEGACY"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)