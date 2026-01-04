"""Effect for EX1_538 in LEGACY"""

def on_play(game, source, target):
    if source.controller.opponent and source.controller.opponent.hero:
        source.controller.opponent.hero.health -= 5