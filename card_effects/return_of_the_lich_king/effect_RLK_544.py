"""Effect for RLK_544 in RETURN_OF_THE_LICH_KING"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'LT22_016P3m', source.zone_position + 1)
    game.summon_token(source.controller, 'LT22_016P3m', source.zone_position + 2)
