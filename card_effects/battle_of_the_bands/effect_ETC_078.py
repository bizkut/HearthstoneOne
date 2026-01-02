"""Effect for ETC_078 in BATTLE_OF_THE_BANDS"""


def battlecry(game, source, target):
    # Bounce Around (FTFY)
    for m in source.controller.board[:]:
        if m != source:
            card = create_card(m.card_id, game)
            card.cost = 1
            source.controller.add_to_hand(card)
            m.destroy()
