"""Effect for MIS_100 in WHIZBANGS_WORKSHOP"""

def on_play(game, source, target):
    if target: target.attack += 5; target.max_health += 5; target.health += 5