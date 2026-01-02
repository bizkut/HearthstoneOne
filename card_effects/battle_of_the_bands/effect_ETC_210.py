"""Effect for ETC_210 in BATTLE_OF_THE_BANDS"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)