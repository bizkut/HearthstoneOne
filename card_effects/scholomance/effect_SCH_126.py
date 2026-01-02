"""Effect for SCH_126 in SCHOLOMANCE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'SCH_126t', source.zone_position + 1)
