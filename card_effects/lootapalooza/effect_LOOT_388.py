"""Effect for LOOT_388 in LOOTAPALOOZA"""

def battlecry(game, source, target):
    if target: game.heal(target, 2)