"""Effect for BOT_066 in BOOMSDAY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'BOT_066t', source.zone_position + 1)
