"""Effect for CORE_ICC_019 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'VAN_skele11', source.zone_position + 1)
