"""Effect for VAN_EX1_622 in VANILLA"""

def on_play(game, source, target):
    if target: target.destroy()