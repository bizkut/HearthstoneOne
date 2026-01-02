"""Effect for DAL_378 in DALARAN"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'DAL_378t1', source.zone_position + 1)
