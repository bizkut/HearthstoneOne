"""Effect for OG_223 in OG"""

def on_play(game, source, target):
    if target: target.max_health += 2; target.health += 2; target.attack += 1