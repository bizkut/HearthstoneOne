"""Effect for CORE_EX1_158 in PLACEHOLDER_202204"""

def on_play(game, source, target):
    if target: target.health = target.max_health; target.attack += 2