"""Effect for ETC_026 in WILD_WEST"""


def battlecry(game, source, target):
    if len(source.controller.board) == 1: # Only self
        player = source.controller
        for ctype in [CardType.SPELL, CardType.MINION, CardType.WEAPON]:
            card = next((c for c in player.deck if c.card_type == ctype), None)
            if card: player.draw_specific_card(card)
