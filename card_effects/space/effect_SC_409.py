"""Effect for SC_409 in SPACE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 1, source)