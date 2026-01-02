"""Effect for CORE_KAR_004 in PLACEHOLDER_202204"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'EX1_160t', source.zone_position + 1)
