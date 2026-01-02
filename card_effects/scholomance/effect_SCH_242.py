"""Effect for SCH_242 in SCHOLOMANCE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'Story_08_Gibberling', source.zone_position + 1)
