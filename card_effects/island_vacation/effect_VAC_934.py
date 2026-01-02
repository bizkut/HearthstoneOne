"""Effect for VAC_934 in ISLAND_VACATION"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 10, source)