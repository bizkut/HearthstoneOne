"""Effect for RLK_654 in RETURN_OF_THE_LICH_KING"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'RLK_654t', source.zone_position + 1)
    game.summon_token(source.controller, 'RLK_654t', source.zone_position + 2)
