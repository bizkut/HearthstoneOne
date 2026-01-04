"""Effect for ETC_385 in BATTLE_OF_THE_BANDS"""

def battlecry(game, source, target):
    source.controller.gain_armor(source.controller.armor)