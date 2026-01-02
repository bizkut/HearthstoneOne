"""Effect for ETC_206 in BATTLE_OF_THE_BANDS"""


def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    spells = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.SPELL]
    if spells: source.controller.add_to_hand(create_card(random.choice(spells), game))
    if source.controller.mana == 0:
         # Simplified: hand back for finale
         pass
