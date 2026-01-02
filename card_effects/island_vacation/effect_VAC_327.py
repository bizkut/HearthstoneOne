"""Effect for VAC_327 in ISLAND_VACATION"""

def battlecry(game, source, target):
    if target: target.attack += 3; target.max_health += 3; target.health += 3; target.frozen = True