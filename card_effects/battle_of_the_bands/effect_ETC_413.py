"""Effect for ETC_413 in BATTLE_OF_THE_BANDS"""

def on_play(game, source, target):
    if target: target.attack += 1; target.max_health += 1; target.health += 1