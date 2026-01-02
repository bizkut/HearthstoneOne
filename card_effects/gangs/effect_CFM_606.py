"""Effect for CFM_606 in GANGS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CFM_606t', source.zone_position + 1)
