"""Effect for WC_036 in THE_BARRENS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'BG31_HERO_811t8_G', source.zone_position + 1)
