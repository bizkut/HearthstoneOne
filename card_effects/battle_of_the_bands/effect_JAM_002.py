"""Effect for JAM_002 in BATTLE_OF_THE_BANDS"""


def on_play(game, source, target):
    import random
    dmg = 5
    while dmg > 0:
        opp = source.controller.opponent.board[:]
        if not opp: break
        t = random.choice(opp)
        game.deal_damage(t, dmg, source)
        dmg -= 1
