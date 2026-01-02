"""Effect for TSC_941 in THE_SUNKEN_CITY"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'PVPDR_BucketList_Naga', source.zone_position + 1)
