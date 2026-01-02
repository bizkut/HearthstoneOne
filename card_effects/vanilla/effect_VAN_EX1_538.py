"""Effect for VAN_EX1_538 in VANILLA"""

def on_play(game, source, target):
    source.controller.opponent.hero.health -= 5