"""Effect for Core_CS2_008 in PLACEHOLDER_202204"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 1, source)