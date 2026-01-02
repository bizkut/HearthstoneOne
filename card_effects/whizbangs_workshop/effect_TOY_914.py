"""Effect for TOY_914 in WHIZBANGS_WORKSHOP"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'LT24_021T1_01am', source.zone_position + 1)
    game.summon_token(source.controller, 'LT24_021T1_01am', source.zone_position + 2)
