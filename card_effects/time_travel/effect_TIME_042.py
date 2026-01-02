"""Effect for TIME_042 in TIME_TRAVEL"""


def battlecry(game, source, target):
    p = source.controller
    while p.hand:
        p.discard(1)
    p.add_to_hand(create_card('TIME_042t', game))
