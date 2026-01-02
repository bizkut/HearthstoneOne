"""Effect for LEG_RLK_077 in LEGACY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'LETL_1113f', source.zone_position + 1)
    game.summon_token(source.controller, 'LETL_1113f', source.zone_position + 2)
