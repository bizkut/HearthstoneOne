"""Effect for CORE_ICC_067 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'PVPDR_Sai_T2at', source.zone_position + 1)
