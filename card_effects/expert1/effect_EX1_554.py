"""Effect for EX1_554 in EXPERT1"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'VAN_EX1_554t', source.zone_position + 1)
    game.summon_token(source.controller, 'VAN_EX1_554t', source.zone_position + 2)
    game.summon_token(source.controller, 'VAN_EX1_554t', source.zone_position + 3)
