"""Effect for CORE_BT_922 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'BT_922t', source.zone_position + 1)
    game.summon_token(source.controller, 'BT_922t', source.zone_position + 2)
