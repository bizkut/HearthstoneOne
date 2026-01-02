"""Effect for LOOT_368 in LOOTAPALOOZA"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'PVPDR_Duels_Buckets_WDemons', source.zone_position + 1)
    game.summon_token(source.controller, 'PVPDR_Duels_Buckets_WDemons', source.zone_position + 2)
    game.summon_token(source.controller, 'PVPDR_Duels_Buckets_WDemons', source.zone_position + 3)
