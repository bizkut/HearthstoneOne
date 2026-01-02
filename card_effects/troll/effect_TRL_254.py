"""Effect for TRL_254 in TROLL"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'UNG_076t1', source.zone_position + 1)
    game.summon_token(source.controller, 'UNG_076t1', source.zone_position + 2)
