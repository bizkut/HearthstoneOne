"""Effect for GVG_116 in GVG"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'FB_Champs_EX1_029', source.zone_position + 1)
