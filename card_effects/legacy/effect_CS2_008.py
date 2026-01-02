"""Effect for CS2_008 in LEGACY"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 1, source)