"""Effect for DAL_088 in DALARAN"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'DAL_088t2', source.zone_position + 1)
