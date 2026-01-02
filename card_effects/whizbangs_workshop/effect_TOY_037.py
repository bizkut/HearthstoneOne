"""Effect for TOY_037 in WHIZBANGS_WORKSHOP"""


def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    secrets = [c.card_id for c in CardDatabase.get_collectible_cards() if 'Secret:' in (c.text or "")]
    if secrets:
        def on_choose(game, cid):
            card = create_card(cid, game)
            card.cost = 1
            game.current_player.add_to_hand(card)
        game.initiate_discover(source.controller, random.sample(secrets, min(3, len(secrets))), on_choose)
