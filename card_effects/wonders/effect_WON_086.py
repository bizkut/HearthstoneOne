"""Effect for WON_086 in WONDERS"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'PRO_001at', source.zone_position + 1)
    game.summon_token(source.controller, 'PRO_001at', source.zone_position + 2)
    game.summon_token(source.controller, 'PRO_001at', source.zone_position + 3)
    game.summon_token(source.controller, 'PRO_001at', source.zone_position + 4)
