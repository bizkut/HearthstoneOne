"""Effect for LOOT_347 in LOOTAPALOOZA"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 3, source)