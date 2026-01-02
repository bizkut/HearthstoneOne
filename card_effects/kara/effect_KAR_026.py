"""Effect for KAR_026 in KARA"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'KAR_026t', source.zone_position + 1)
