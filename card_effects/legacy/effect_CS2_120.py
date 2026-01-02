"""Effect for CS2_120 in LEGACY"""

def battlecry(game, source, target):
    if target: target.attack += 1; target.health += 1