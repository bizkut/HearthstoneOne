"""Effect for OG_094 in OG"""

def on_play(game, source, target):
    if target: target.max_health += 6; target.health += 6; target.attack += 2