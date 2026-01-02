"""Effect for VAC_936 in ISLAND_VACATION"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)