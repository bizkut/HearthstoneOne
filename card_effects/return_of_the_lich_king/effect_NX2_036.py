"""Effect for NX2_036 in RETURN_OF_THE_LICH_KING"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'PVPDR_BucketList_Undead', source.zone_position + 1)
