"""Effect for JAM_013 in BATTLE_OF_THE_BANDS"""

def on_play(game, source, target):
    if target:
        target.attack += 3; target.max_health += 3; target.health += 3