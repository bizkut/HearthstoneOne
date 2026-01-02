"""Effect for FIR_901 in EMERALD_DREAM"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'DALA_Warrior_07', source.zone_position + 1)
    game.summon_token(source.controller, 'DALA_Warrior_07', source.zone_position + 2)
