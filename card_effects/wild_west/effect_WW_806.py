"""Effect for WW_806 in WILD_WEST"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'VAN_EX1_554t', source.zone_position + 1)
    game.summon_token(source.controller, 'VAN_EX1_554t', source.zone_position + 2)
