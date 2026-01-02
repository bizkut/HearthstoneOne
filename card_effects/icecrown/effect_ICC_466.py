"""Effect for ICC_466 in ICECROWN"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'FB_Champs_ICC_466', source.zone_position + 1)
