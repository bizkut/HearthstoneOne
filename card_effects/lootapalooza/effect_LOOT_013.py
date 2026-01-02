"""Effect for LOOT_013 in LOOTAPALOOZA"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)