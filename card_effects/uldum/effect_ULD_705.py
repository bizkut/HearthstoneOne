"""Effect for ULD_705 in ULDUM"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'ULD_705t', source.zone_position + 1)
