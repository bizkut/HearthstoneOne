"""Effect for ULD_174 in ULDUM"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'ULD_174t', source.zone_position + 1)
