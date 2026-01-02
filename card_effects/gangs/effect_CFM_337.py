"""Effect for CFM_337 in GANGS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CFM_337t', source.zone_position + 1)
