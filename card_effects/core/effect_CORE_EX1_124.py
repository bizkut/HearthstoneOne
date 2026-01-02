"""Effect for CORE_EX1_124 in CORE"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)