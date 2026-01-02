"""Effect for ULD_190 in ULDUM"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 5, source)