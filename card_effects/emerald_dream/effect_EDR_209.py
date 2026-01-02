"""Effect for EDR_209 in EMERALD_DREAM"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TRL_341t', source.zone_position + 1)
