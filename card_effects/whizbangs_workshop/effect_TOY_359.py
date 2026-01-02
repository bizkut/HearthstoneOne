"""Effect for TOY_359 in WHIZBANGS_WORKSHOP"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)