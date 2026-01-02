"""Effect for TOY_606 in WHIZBANGS_WORKSHOP"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 8, source)