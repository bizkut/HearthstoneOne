from simulator.enums import CardType
"""Effect for ETC_418 in BATTLE_OF_THE_BANDS"""


def battlecry(game, source, target):
    w = next((c for c in source.controller.deck if c.card_type == CardType.WEAPON), None)
    if w: source.controller.draw_specific_card(w)
