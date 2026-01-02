"""Effect for ETC_087 in BATTLE_OF_THE_BANDS"""


def battlecry(game, source, target):
    source.controller.max_hand_size = 11
    # Simplified: no max mana 11 yet
