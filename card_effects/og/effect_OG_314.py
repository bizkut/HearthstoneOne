"""Effect for OG_314 in OG"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'OG_314b', source.zone_position + 1)
