"""Effect for BOT_565 in BOOMSDAY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'OG_156a', source.zone_position + 1)
