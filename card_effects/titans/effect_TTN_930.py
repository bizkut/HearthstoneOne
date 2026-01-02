"""Effect for TTN_930 in TITANS"""

def on_play(game, source, target):
    source.controller.hero.gain_armor(5)