"""Effect for WON_070 in WONDERS"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'CFM_712_t30', source.zone_position + 1)
