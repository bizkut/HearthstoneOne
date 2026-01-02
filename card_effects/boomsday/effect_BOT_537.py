"""Effect for BOT_537 in BOOMSDAY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TB_BaconUps_039t', source.zone_position + 1)
