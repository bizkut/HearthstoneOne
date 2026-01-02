"""Effect for CS2_029 in LEGACY"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 6, source)