"""Effect for TIME_008 in TIME_TRAVEL"""


def battlecry(game, source, target):
    source.controller.discard(1)
    source.controller.opponent.discard(1)
    # Rewind placeholder
    source.controller.draw(1)
