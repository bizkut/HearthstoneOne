"""Effect for WON_067 in WONDERS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CFM_712_t30', source.zone_position + 1)
