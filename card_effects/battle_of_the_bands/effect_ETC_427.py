"""Effect for ETC_427 in BATTLE_OF_THE_BANDS"""

def on_play(game, source, target):
    if target: target.attack += 2; target.max_health += 2; target.health += 2