"""Effect for TTN_861 in TITANS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TRLA_Shaman_06', source.zone_position + 1)
    game.summon_token(source.controller, 'TRLA_Shaman_06', source.zone_position + 2)
