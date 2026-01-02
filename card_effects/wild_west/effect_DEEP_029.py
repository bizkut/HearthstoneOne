"""Effect for DEEP_029 in WILD_WEST"""


def on_play(game, source, target):
    # Finale condition simplified
    if source.controller.mana == 0:
        for _ in range(source.controller.mana_crystals):
            opp = source.controller.opponent.board + [source.controller.opponent.hero]
            import random
            game.deal_damage(random.choice(opp), 1, source)
