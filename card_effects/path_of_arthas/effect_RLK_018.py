"""Effect for RLK_018 in PATH_OF_ARTHAS"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'RLK_060t', source.zone_position + 1)
