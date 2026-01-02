"""Effect for VAN_CS2_008 in VANILLA"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 1, source)