"""Effect for CORE_UNG_941 in CORE"""

def on_play(game, source, target):
    player = source.controller
    from simulator.card_loader import CardDatabase
    spells = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.SPELL]
    import random
    options = random.sample(spells, 3)
    def on_choose(game, card_id):
        c = create_card(card_id, game)
        c.cost -= 2
        game.current_player.add_to_hand(c)
    game.initiate_discover(player, options, on_choose)