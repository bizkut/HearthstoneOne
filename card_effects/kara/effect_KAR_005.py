"""Effect for KAR_005 in KARA"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TB_BaconUps_004t', source.zone_position + 1)
