"""Effect for SW_422 in STORMWIND"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'VAN_EX1_tk9b', source.zone_position + 1)
