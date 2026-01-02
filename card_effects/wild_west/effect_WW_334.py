"""Effect for WW_334 in WILD_WEST"""

def on_play(game, source, target):
    source.controller.hero.gain_armor(6)