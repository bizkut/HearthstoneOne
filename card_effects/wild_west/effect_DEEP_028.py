"""Effect for DEEP_028 in WILD_WEST"""


def on_play(game, source, target):
    # Gain mana crystals, then summon if full
    source.controller.mana_crystals = min(10, source.controller.mana_crystals + 3)
    # Simple summon logic
    source.controller.summon(create_card('DEEP_028t', game))
