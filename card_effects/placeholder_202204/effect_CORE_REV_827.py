"""Effect for CORE_REV_827 in PLACEHOLDER_202204"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'OG_216a', source.zone_position + 1)
