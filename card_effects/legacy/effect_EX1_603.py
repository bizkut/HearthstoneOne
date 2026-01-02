"""Effect for EX1_603 in LEGACY"""

def on_play(game, source, target):
    if target: target.attack += 2; target.controller.hero.take_damage(-2)