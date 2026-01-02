"""Effect for CORE_EX1_194 in PLACEHOLDER_202204"""

def on_play(game, source, target):
    if target: target.max_health += 6; target.health += 6; target.attack += 2