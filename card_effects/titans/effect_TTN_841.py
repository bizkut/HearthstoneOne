"""Effect for TTN_841 in TITANS"""


def on_play(game, source, target):
    source.controller.hero.attack += 4
