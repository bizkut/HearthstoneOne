"""Effect for DEEP_018 in WILD_WEST"""


def on_play(game, source, target):
    if target: target.divine_shield = True
    source.controller.draw(1) # Simplified Excavate
