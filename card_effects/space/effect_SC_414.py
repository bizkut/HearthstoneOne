"""Effect for SC_414 in SPACE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 5, source)