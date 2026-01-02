"""Effect for VAN_EX1_259 in VANILLA"""

def on_play(game, source, target):
    if target: target.transform('EX1_259t')