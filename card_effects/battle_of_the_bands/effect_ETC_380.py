"""Effect for ETC_380 in BATTLE_OF_THE_BANDS"""


def on_play(game, source, target):
    # Armor Up (Simplified Warrior spell)
    source.controller.hero.gain_armor(10)
