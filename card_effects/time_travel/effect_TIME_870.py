"""Effect for TIME_870 in TIME_TRAVEL"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'TRL_309t', source.zone_position + 1)
