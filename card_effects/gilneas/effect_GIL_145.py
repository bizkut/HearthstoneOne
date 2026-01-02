"""Effect for GIL_145 in GILNEAS"""

def on_play(game, source, target):
    if target: target.max_health += 2; target.health += 2; target.attack += 1