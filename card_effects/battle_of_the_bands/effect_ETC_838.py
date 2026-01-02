"""Effect for ETC_838 in BATTLE_OF_THE_BANDS"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'CUSTOM_TOKEN', 0)