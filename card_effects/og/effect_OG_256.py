"""Effect for OG_256 in OG"""

def battlecry(game, source, target):
    for m in source.controller.board[:]: m.max_health += 1; m.health += 1; m.attack += 1