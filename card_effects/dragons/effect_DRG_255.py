"""Effect for DRG_255 in DRAGONS"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'FB_Champs_EX1_029', source.zone_position + 1)
    game.summon_token(source.controller, 'FB_Champs_EX1_029', source.zone_position + 2)
    game.summon_token(source.controller, 'FB_Champs_EX1_029', source.zone_position + 3)
