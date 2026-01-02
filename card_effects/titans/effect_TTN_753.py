"""Effect for TTN_753 in TITANS"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)