"""Effect for AT_099 in TGT"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'LETL_819H2', source.zone_position + 1)
