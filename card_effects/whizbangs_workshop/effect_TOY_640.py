"""Effect for TOY_640 in WHIZBANGS_WORKSHOP"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)