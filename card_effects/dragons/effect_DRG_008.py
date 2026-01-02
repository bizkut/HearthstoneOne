"""Effect for DRG_008 in DRAGONS"""

def on_play(game, source, target):
    for m in source.controller.board[:]: m.max_health += 1; m.health += 1; m.attack += 1