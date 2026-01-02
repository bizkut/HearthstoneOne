"""Effect for CORE_EX1_603 in PLACEHOLDER_202204"""

def on_play(game, source, target):
    if target: target.attack += 2; target.controller.hero.take_damage(-2)