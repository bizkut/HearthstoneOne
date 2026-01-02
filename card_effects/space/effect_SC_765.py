"""Effect for SC_765 in SPACE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)