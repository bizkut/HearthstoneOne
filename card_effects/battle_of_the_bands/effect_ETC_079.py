"""Effect for ETC_079 in BATTLE_OF_THE_BANDS"""


def on_play(game, source, target):
    p = source.controller
    for m in p.board[:]:
        if m != source:
            card = create_card(m.card_id, game)
            card.cost = 1
            p.add_to_hand(card)
            m.destroy()
