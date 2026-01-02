"""Effect for ULD_712 in ULDUM"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'ULD_430t', source.zone_position + 1)
