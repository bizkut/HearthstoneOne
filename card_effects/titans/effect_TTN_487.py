"""Effect for TTN_487 in TITANS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'DRG_091t', source.zone_position + 1)
