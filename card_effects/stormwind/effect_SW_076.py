"""Effect for SW_076 in STORMWIND"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'SW_076t', source.zone_position + 1)
    game.summon_token(source.controller, 'SW_076t', source.zone_position + 2)
