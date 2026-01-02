"""Effect for CORE_DMF_238 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'DMF_238t', source.zone_position + 1)
