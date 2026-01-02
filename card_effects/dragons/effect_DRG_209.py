"""Effect for DRG_209 in DRAGONS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'DRG_209t', source.zone_position + 1)
