"""Effect for GIL_577 in GILNEAS"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'TB_BaconUps_027t', source.zone_position + 1)
