"""Effect for EDR_492 in EMERALD_DREAM"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'EDR_492t', source.zone_position + 1)
    game.summon_token(source.controller, 'EDR_492t', source.zone_position + 2)
    game.summon_token(source.controller, 'EDR_492t', source.zone_position + 3)
