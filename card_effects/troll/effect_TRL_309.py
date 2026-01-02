"""Effect for TRL_309 in TROLL"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TRL_309t', source.zone_position + 1)
