"""Effect for TOY_358 in WHIZBANGS_WORKSHOP"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'EX1_538t', source.zone_position + 1)
