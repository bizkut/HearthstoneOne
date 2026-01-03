from simulator.enums import CardType
"""Effect for VAC_438 in ISLAND_VACATION"""


def battlecry(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    locs = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.LOCATION]
    if locs:
        def on_choose(game, cid):
            game.current_player.add_to_hand(create_card(cid, game))
        game.initiate_discover(source.controller, random.sample(locs, min(3, len(locs))), on_choose)
