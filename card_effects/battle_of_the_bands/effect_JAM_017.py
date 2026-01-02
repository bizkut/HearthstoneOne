"""Effect for JAM_017 in BATTLE_OF_THE_BANDS"""

def on_play(game, source, target):
    if target: setattr(target, 'rush', True)