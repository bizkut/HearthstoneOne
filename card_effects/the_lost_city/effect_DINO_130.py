"""Effect for DINO_130 in THE_LOST_CITY"""

def battlecry(game, source, target):
    for m in source.controller.board[:]: m.max_health += 1; m.health += 1; m.attack += 1