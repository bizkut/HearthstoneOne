"""Effect for WW_810 in WILD_WEST"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'WW_810t8', source.zone_position + 1)
