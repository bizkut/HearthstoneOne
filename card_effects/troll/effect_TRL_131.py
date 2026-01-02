"""Effect for TRL_131 in TROLL"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'RLK_060t', source.zone_position + 1)
