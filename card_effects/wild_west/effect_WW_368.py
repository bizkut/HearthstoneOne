"""Effect for WW_368 in WILD_WEST"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'PVPDR_BucketList_Undead', source.zone_position + 1)
    game.summon_token(source.controller, 'PVPDR_BucketList_Undead', source.zone_position + 2)
    game.summon_token(source.controller, 'PVPDR_BucketList_Undead', source.zone_position + 3)
    game.summon_token(source.controller, 'PVPDR_BucketList_Undead', source.zone_position + 4)
