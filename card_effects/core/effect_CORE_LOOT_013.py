"""Effect for CORE_LOOT_013 in CORE"""

def battlecry(game, source, target):
    if target: game.deal_damage(target, 2, source)