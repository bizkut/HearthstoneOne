"""Effect for SW_439 in STORMWIND"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'VAN_EX1_tk28', source.zone_position + 1)
