"""Effect for BAR_327 in THE_BARRENS"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'PVPDR_Duels_Buckets_WDemons', source.zone_position + 1)
    game.summon_token(source.controller, 'PVPDR_Duels_Buckets_WDemons', source.zone_position + 2)
