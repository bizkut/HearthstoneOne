"""Effect for TTN_850 in TITANS"""


def battlecry(game, source, target):
    for _ in range(3):
        source.controller.opponent.add_to_deck(create_card('TTN_850t', game))
