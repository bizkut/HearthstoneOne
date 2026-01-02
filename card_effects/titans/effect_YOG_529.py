"""Effect for YOG_529 in TITANS"""

def on_play(game, source, target):
    source.controller.hero.gain_armor(5)