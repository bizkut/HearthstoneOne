"""Effect for ETC_314 in BATTLE_OF_THE_BANDS"""

def on_play(game, source, target):
    for p in game.players:
        for m in p.board[:]: game.deal_damage(m, 3, source)