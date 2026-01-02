"""Effect for VAN_DS1_184 in VANILLA"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)