"""Effect for CORE_REV_307 in PLACEHOLDER_202204"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'VAN_EX1_tk9b', source.zone_position + 1)
