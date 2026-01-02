"""Effect for SCH_710 in SCHOLOMANCE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'VAN_skele11', source.zone_position + 1)
