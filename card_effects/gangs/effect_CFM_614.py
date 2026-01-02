"""Effect for CFM_614 in GANGS"""

def on_play(game, source, target):
    for m in source.controller.board[:]: m.max_health += 1; m.health += 1; m.attack += 1