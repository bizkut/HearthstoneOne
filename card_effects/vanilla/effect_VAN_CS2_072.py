"""Effect for VAN_CS2_072 in VANILLA"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)