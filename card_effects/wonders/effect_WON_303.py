"""Effect for WON_303 in WONDERS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CFM_712_t30', source.zone_position + 1)
