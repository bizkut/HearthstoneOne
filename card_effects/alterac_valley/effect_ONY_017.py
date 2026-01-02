"""Effect for ONY_017 in ALTERAC_VALLEY"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'KAR_010a', source.zone_position + 1)
    game.summon_token(source.controller, 'KAR_010a', source.zone_position + 2)
