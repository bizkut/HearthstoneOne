"""Effect for TTN_803 in TITANS"""

def on_play(game, source, target):
    if target: target.attack += 3; target.max_health += 3; target.health += 3