"""Effect for SCH_243 in SCHOLOMANCE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TUTR_NEW1_012t2', source.zone_position + 1)
    game.summon_token(source.controller, 'TUTR_NEW1_012t2', source.zone_position + 2)
