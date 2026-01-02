"""Effect for CORE_ICC_085 in PLACEHOLDER_202204"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'PVPDR_Sai_T2at', source.zone_position + 1)
