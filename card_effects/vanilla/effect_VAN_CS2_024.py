"""Effect for VAN_CS2_024 in VANILLA"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 3, source); target.frozen = True