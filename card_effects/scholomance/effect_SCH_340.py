"""Effect for SCH_340 in SCHOLOMANCE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'SCH_340t', source.zone_position + 1)
