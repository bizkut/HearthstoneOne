"""Effect for GIL_596 in GILNEAS"""

def battlecry(game, source, target):
    for m in source.controller.board[:]: m.max_health += 1; m.health += 1; m.attack += 1