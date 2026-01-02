"""Effect for DRG_251 in DRAGONS"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'DRG_251t', source.zone_position + 1)
