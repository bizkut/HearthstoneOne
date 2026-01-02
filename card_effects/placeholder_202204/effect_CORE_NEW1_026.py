"""Effect for CORE_NEW1_026 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'VAN_NEW1_026t', source.zone_position + 1)
