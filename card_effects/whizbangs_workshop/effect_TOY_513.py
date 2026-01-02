"""Effect for TOY_513 in WHIZBANGS_WORKSHOP"""

def battlecry(game, source, target):
    if target: target.attack += 1; target.max_health += 1; target.health += 1