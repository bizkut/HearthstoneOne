"""Effect for BAR_534 in THE_BARRENS"""

def on_play(game, source, target):
    for m in source.controller.board[:]: m.max_health += 3; m.health += 3; m.attack += 1