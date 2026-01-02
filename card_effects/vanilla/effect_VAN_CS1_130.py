"""Effect for VAN_CS1_130 in VANILLA"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)