"""Effect for TLC_833 in THE_LOST_CITY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'LOOT_153t1', source.zone_position + 1)
