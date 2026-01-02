"""Effect for TRL_507 in TROLL"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'TB_015', source.zone_position + 1)
