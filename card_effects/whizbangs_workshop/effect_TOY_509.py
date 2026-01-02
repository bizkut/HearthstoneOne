"""Effect for TOY_509 in WHIZBANGS_WORKSHOP"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)