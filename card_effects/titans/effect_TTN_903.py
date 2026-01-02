"""Effect for TTN_903 in TITANS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TRL_341t', source.zone_position + 1)
