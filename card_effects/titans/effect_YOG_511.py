from simulator.enums import CardType
"""Effect for YOG_511 in TITANS"""


def battlecry(game, source, target):
    player = source.controller
    from simulator.card_loader import CardDatabase
    weapons = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.WEAPON]
    import random
    chosen = random.sample(weapons, min(3, len(weapons)))
    def on_choose(game, cid):
        card = create_card(cid, game)
        game.current_player.add_to_hand(card)
    game.initiate_discover(player, chosen, on_choose)
