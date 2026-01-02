"""Effect for VAN_CS2_120 in VANILLA"""

def battlecry(game, source, target):
    if target: target.attack += 1; target.health += 1