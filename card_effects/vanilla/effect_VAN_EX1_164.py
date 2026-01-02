"""Effect for VAN_EX1_164 in VANILLA"""

def on_play(game, source, target):
    if target: target.frozen = True; game.deal_damage(target, 4, source)