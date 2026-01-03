from simulator.enums import CardType
"""Effect for TOY_046 in WHIZBANGS_WORKSHOP"""


def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    options = [c.card_id for c in CardDatabase.get_collectible_cards() if c.cost == 4 and c.card_type == CardType.MINION]
    if options:
        def on_choose(game, cid):
            card = create_card(cid, game)
            card.attack = 7; card.max_health = 7; card.health = 7
            game.current_player.add_to_hand(card)
        game.initiate_discover(source.controller, random.sample(options, min(3, len(options))), on_choose)
