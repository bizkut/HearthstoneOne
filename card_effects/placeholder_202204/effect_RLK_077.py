"""Effect for RLK_077 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'LETL_1113f', source.zone_position + 1)
    game.summon_token(source.controller, 'LETL_1113f', source.zone_position + 2)
