"""Effect for SW_026 in STORMWIND"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'VAN_EX1_tk11', source.zone_position + 1)
