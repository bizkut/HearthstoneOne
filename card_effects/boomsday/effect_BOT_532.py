"""Effect for BOT_532 in BOOMSDAY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'BOT_031_Puzzle', source.zone_position + 1)
    game.summon_token(source.controller, 'BOT_031_Puzzle', source.zone_position + 2)
