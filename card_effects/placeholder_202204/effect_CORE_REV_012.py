"""Effect for CORE_REV_012 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'REV_012t', source.zone_position + 1)
