"""Effect for LOOT_132 in LOOTAPALOOZA"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 6, source)