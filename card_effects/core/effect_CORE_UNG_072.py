"""Effect for CORE_UNG_072 in CORE"""

def battlecry(game, source, target):
    player = source.controller
    from simulator.card_loader import CardDatabase
    taunts = [c.card_id for c in CardDatabase.get_collectible_cards() if c.taunt and c.card_type == CardType.MINION]
    import random
    options = random.sample(taunts, 3)
    def on_choose(game, card_id):
        game.current_player.add_to_hand(create_card(card_id, game))
    game.initiate_discover(player, options, on_choose)