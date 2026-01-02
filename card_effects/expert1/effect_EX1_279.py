"""Effect for EX1_279 in EXPERT1"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 10, source)