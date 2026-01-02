"""Effect for LEG_RLK_226 in LEGACY"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'RLK_Prologue_RLK_226t', source.zone_position + 1)
