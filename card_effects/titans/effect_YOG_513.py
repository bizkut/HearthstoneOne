"""Effect for YOG_513 in TITANS"""

def on_play(game, source, target):
    if target: target.attack += 2; target.max_health += 2; target.health += 2