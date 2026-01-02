"""Effect for ULD_271 in ULDUM"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)