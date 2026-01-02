"""Effect for TRL_347 in TROLL"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'VAN_EX1_tk29', source.zone_position + 1)
