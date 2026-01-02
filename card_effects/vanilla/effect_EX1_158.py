"""Effect for EX1_158 in VANILLA"""

def on_play(game, source, target):
    if target: target.health = target.max_health; target.attack += 2