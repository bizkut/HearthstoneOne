"""Effect for VAC_425 in ISLAND_VACATION"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)