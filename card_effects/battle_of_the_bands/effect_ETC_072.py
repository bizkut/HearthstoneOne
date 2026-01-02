"""Effect for ETC_072 in BATTLE_OF_THE_BANDS"""


def on_play(game, source, target):
    if source.controller.cards_played_this_turn:
        for _ in range(4):
            opp = source.controller.opponent.board + [source.controller.opponent.hero]
            import random
            game.deal_damage(random.choice(opp), 1, source)
