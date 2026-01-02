"""Effect for CORE_ICC_838 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'NAX14_03', source.zone_position + 1)
    game.summon_token(source.controller, 'NAX14_03', source.zone_position + 2)
