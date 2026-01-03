from simulator.enums import CardType
"""Effect for VAC_335 in ISLAND_VACATION"""


def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    spells = [c.card_id for c in CardDatabase.get_collectible_cards() 
              if c.card_type == CardType.SPELL and c.cost == 1 and c.card_class != source.controller.hero.data.card_class]
    if spells:
        for _ in range(2):
            source.controller.add_to_hand(create_card(random.choice(spells), game))
