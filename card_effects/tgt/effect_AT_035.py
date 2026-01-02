"""Effect for AT_035 in TGT"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'WON_076t', source.zone_position + 1)
