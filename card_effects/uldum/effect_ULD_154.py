"""Effect for ULD_154 in ULDUM"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'ULD_154t', source.zone_position + 1)
    game.summon_token(source.controller, 'ULD_154t', source.zone_position + 2)
