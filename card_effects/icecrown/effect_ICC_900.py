"""Effect for ICC_900 in ICECROWN"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'PVPDR_Sai_T2at', source.zone_position + 1)
