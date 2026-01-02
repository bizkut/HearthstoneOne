"""Effect for CORE_REV_356 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TRL_020t', source.zone_position + 1)
