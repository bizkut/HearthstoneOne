"""Effect for WW_027 in WILD_WEST"""

def on_play(game, source, target):
    if target: target.attack += 2; target.max_health += 3; target.health += 3