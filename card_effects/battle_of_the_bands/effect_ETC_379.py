"""Effect for ETC_379 in BATTLE_OF_THE_BANDS"""

def on_play(game, source, target):
    source.controller.hero.gain_armor(4)