"""Effect for BOT_535 in BOOMSDAY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TB_BaconUps_032t', source.zone_position + 1)
    game.summon_token(source.controller, 'TB_BaconUps_032t', source.zone_position + 2)
