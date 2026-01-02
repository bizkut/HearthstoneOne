"""Effect for DEEP_034 in WILD_WEST"""


def battlecry(game, source, target):
    # Condition: if played elemental last turn
    source.controller.draw(1)
