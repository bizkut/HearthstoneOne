"""Effect for CORE_ICC_026 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'VAN_skele11', source.zone_position + 1)
    game.summon_token(source.controller, 'VAN_skele11', source.zone_position + 2)
