"""Effect for WORK_022 in ISLAND_VACATION"""

def on_play(game, source, target):
    if target: target.attack += 1; target.max_health += 1; target.health += 1