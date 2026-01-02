"""Effect for EX1_538 in LEGACY"""

def on_play(game, source, target):
    source.controller.opponent.hero.health -= 5