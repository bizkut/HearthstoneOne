"""Effect for TIME_032 in TIME_TRAVEL"""


def battlecry(game, source, target):
    p = source.controller
    opp = p.opponent
    deck = sorted(p.deck, key=lambda x: x.cost, reverse=True)
    if len(deck) >= 2:
        high = deck[:2]
        for c in high: p.draw_specific_card(c)
    deck_new = sorted(p.deck, key=lambda x: x.cost)
    if len(deck_new) >= 2:
        low = deck_new[:2]
        for c in low:
             p.deck.remove(c)
             opp.add_to_hand(c)
