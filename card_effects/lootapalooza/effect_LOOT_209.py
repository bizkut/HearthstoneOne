"""Effect for LOOT_209 in LOOTAPALOOZA"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'DALA_Warrior_07', source.zone_position + 1)
