"""Effect for CFM_902 in GANGS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CFM_712_t30', source.zone_position + 1)
