"""Effect for ICC_026 in ICECROWN"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'VAN_skele11', source.zone_position + 1)
    game.summon_token(source.controller, 'VAN_skele11', source.zone_position + 2)
