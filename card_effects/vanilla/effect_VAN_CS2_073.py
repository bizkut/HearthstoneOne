"""Effect for VAN_CS2_073 in VANILLA"""

def on_play(game, source, target):
    if target: target.attack += 2