"""Effect for BT_922 in DEMON_HUNTER_INITIATE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'BT_922t', source.zone_position + 1)
    game.summon_token(source.controller, 'BT_922t', source.zone_position + 2)
