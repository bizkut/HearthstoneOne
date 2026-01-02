"""Effect for ETC_088 in BATTLE_OF_THE_BANDS"""


def battlecry(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    spells = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.SPELL]
    if spells:
        def on_choose(game, cid):
            game.current_player.add_to_hand(create_card(cid, game))
            if source.controller.mana == 0:
                 # Finale: second discovery
                 game.initiate_discover(source.controller, random.sample(spells, 3), lambda g, c: g.current_player.add_to_hand(create_card(c, g)))
        game.initiate_discover(source.controller, random.sample(spells, min(3, len(spells))), on_choose)
