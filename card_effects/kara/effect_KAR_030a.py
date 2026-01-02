"""Effect for KAR_030a in KARA"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'OG_216a', source.zone_position + 1)
