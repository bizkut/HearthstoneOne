"""Effect for WORK_021 in ISLAND_VACATION"""

def on_play(game, source, target):
    if target: target.attack += 4; target.max_health += 4; target.health += 4