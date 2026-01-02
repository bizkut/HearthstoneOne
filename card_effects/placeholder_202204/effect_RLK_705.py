"""Effect for RLK_705 in PLACEHOLDER_202204"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'RLK_060t', source.zone_position + 1)
    game.summon_token(source.controller, 'RLK_060t', source.zone_position + 2)
