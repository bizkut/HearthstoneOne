"""Effect for DEEP_007 in WILD_WEST"""


def battlecry(game, source, target):
    # Sir Finley - simplified transform
    for m in source.controller.opponent.board[:]:
        m.transform('CS2_168')
