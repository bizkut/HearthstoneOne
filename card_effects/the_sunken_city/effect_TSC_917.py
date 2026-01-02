"""Effect for TSC_917 in THE_SUNKEN_CITY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'PVPDR_BucketList_Naga', source.zone_position + 1)
