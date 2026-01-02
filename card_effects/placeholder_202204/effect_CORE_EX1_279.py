"""Effect for CORE_EX1_279 in PLACEHOLDER_202204"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 10, source)