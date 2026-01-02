"""Effect for TOY_877 in WHIZBANGS_WORKSHOP"""

def on_play(game, source, target):
    if target: target.attack += 2; target.max_health += 3; target.health += 3