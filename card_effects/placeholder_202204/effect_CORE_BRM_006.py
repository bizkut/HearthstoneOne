"""Effect for CORE_BRM_006 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'EX1_316t', source.zone_position + 1)
