"""Effect for TIME_875 in TIME_TRAVEL"""


def battlecry(game, source, target):
    opp = source.controller.opponent
    # Kill Llane placeholder
    opp.hero.health //= 2
