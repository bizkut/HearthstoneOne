"""Effect for TOY_716 in WHIZBANGS_WORKSHOP"""

def on_play(game, source, target):
    for m in source.controller.board[:]: m.max_health += 2; m.health += 2; m.attack += 1