"""Effect for ETC_528 in BATTLE_OF_THE_BANDS"""


def on_play(game, source, target):
    beams = source.controller.lightshow_count = getattr(source.controller, 'lightshow_count', 0) + 1
    for _ in range(beams):
        opp = source.controller.opponent.board + [source.controller.opponent.hero]
        import random
        game.deal_damage(random.choice(opp), 2, source)
