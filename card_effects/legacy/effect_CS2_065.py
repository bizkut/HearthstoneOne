"""Effect for CS2_065 in LEGACY"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 3, source)