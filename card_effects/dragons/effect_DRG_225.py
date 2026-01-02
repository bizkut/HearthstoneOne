"""Effect for DRG_225 in DRAGONS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'DRG_225t', source.zone_position + 1)
    game.summon_token(source.controller, 'DRG_225t', source.zone_position + 2)
