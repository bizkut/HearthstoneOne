"""Effect for OG_061 in OG"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'OG_061t', source.zone_position + 1)
