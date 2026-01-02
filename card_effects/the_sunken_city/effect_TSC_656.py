"""Effect for TSC_656 in THE_SUNKEN_CITY"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'UNG_999t2t1', source.zone_position + 1)
