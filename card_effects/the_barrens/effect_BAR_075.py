"""Effect for BAR_075 in THE_BARRENS"""

def battlecry(game, source, target):
    for m in source.controller.board[:]: m.max_health += 1; m.health += 1; m.attack += 1