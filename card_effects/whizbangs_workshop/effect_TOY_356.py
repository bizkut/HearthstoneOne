"""Effect for TOY_356 in WHIZBANGS_WORKSHOP"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 7, source)