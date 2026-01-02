"""Effect for TTN_925 in TITANS"""


def battlecry(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    spells = [c.card_id for c in CardDatabase.get_collectible_cards() 
              if c.card_type == CardType.SPELL and c.cost <= 3 and c.card_class != source.controller.hero.data.card_class]
    if spells:
        def on_choose(game, cid):
            game.current_player.add_to_hand(create_card(cid, game))
        game.initiate_discover(source.controller, random.sample(spells, min(3, len(spells))), on_choose)
