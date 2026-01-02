"""Effect for CFM_343 in GANGS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CFM_712_t30', source.zone_position + 1)
