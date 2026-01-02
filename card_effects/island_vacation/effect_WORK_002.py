"""Effect for WORK_002 in ISLAND_VACATION"""

def battlecry(game, source, target):
    if target: target.attack += 1; target.max_health += 1; target.health += 1