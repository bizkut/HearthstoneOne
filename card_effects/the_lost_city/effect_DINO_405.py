"""Effect for DINO_405 in THE_LOST_CITY"""

def on_play(game, source, target):
    for m in source.controller.board[:]: m.max_health += 2; m.health += 2; m.attack += 2