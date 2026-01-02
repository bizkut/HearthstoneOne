"""Effect for TOY_646 in WHIZBANGS_WORKSHOP"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)