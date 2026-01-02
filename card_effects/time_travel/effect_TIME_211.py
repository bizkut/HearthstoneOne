"""Effect for TIME_211 in TIME_TRAVEL"""


def on_play(game, source, target):
    # Simplified Choose One
    import random
    if random.random() > 0.5:
        # Empower Zin-Azshari (Buff all board?)
        for m in source.controller.board: m.attack += 2; m.health += 2
    else:
        # Well of Eternity (Restore mana/health?)
        source.controller.mana = source.controller.max_mana
