"""Effect for VAN_EX1_538 in VANILLA"""

def on_play(game, source, target):
    if source.controller.opponent and source.controller.opponent.hero:
        source.controller.opponent.hero.health -= 5