"""Effect for TOY_825 in WHIZBANGS_WORKSHOP"""

def on_play(game, source, target):
    if target: target.attack += 1; target.max_health += 1; target.health += 1