"""Effect for KAR_004 in KARA"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'EX1_160t', source.zone_position + 1)
