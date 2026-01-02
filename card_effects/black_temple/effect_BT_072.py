"""Effect for BT_072 in BLACK_TEMPLE"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'VAC_509t', source.zone_position + 1)
    game.summon_token(source.controller, 'VAC_509t', source.zone_position + 2)
