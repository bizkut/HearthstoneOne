"""Effect for ETC_077 in BATTLE_OF_THE_BANDS"""


def on_play(game, source, target):
    if source.controller.cards_played_this_turn:
        from simulator.card_loader import CardDatabase
        import random
        combos = [c.card_id for c in CardDatabase.get_collectible_cards() if 'Combo:' in (c.text or "")]
        if combos: source.controller.add_to_hand(create_card(random.choice(combos), game))
