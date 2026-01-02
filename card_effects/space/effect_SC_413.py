"""Effect for SC_413 in SPACE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 10, source)