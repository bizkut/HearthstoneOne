"""Effect for TTN_734 in TITANS"""

def battlecry(game, source, target):
    if target: target.attack += 2; target.max_health += 2; target.health += 2