"""Effect for DAL_566 in DALARAN"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'DAL_566t', source.zone_position + 1)
    game.summon_token(source.controller, 'DAL_566t', source.zone_position + 2)
    game.summon_token(source.controller, 'DAL_566t', source.zone_position + 3)
    game.summon_token(source.controller, 'DAL_566t', source.zone_position + 4)
