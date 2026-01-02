"""Effect for BRM_022 in BRM"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'KAR_010a', source.zone_position + 1)
