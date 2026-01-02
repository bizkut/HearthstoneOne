"""Effect for RLK_063 in PATH_OF_ARTHAS"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'TUTR_RLK_063t', source.zone_position + 1)
