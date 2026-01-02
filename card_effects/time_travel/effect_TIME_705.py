"""Effect for TIME_705 in TIME_TRAVEL"""


def battlecry(game, source, target):
    # Set bottom 5 costs to 1
    for c in source.controller.deck[-5:]:
        c.cost = 1
