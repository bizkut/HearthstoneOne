from simulator.enums import CardType
"""Effect for ETC_417 in BATTLE_OF_THE_BANDS"""


def on_play(game, source, target):
    for c in source.controller.deck:
        if c.card_type == CardType.MINION:
            c.attack += c.cost; c.health += c.cost; c.max_health += c.cost
