"""Effect for VAC_947 in ISLAND_VACATION"""

def battlecry(game, source, target):
    if target: target.attack += 1; target.max_health += 1; target.health += 1