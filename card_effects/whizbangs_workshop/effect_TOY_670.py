"""Effect for TOY_670 in WHIZBANGS_WORKSHOP"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'ULDA_Reno_05', source.zone_position + 1)
    game.summon_token(source.controller, 'ULDA_Reno_05', source.zone_position + 2)
