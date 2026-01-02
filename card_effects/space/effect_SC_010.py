"""Effect for SC_010 in SPACE"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'BG31_HERO_811t2_G', source.zone_position + 1)
