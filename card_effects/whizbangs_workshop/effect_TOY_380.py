"""Effect for TOY_380 in WHIZBANGS_WORKSHOP"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'KAR_010a', source.zone_position + 1)
