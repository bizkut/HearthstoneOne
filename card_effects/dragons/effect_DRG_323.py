"""Effect for DRG_323 in DRAGONS"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'DALA_Warrior_07', source.zone_position + 1)
