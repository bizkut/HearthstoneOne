"""Effect for CORE_REV_314 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'KAR_010a', source.zone_position + 1)
