"""Effect for BOT_407 in BOOMSDAY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'BOT_102t', source.zone_position + 1)
    game.summon_token(source.controller, 'BOT_102t', source.zone_position + 2)
