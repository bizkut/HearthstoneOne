"""Effect for DAL_087 in DALARAN"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TB_BaconShop_HP_033t_G', source.zone_position + 1)
    game.summon_token(source.controller, 'TB_BaconShop_HP_033t_G', source.zone_position + 2)
