"""Effect for ETC_083 in BATTLE_OF_THE_BANDS"""
from simulator.enums import Race


def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    demons = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.DEMON]
    if demons:
        def on_choose(game, cid):
            card = create_card(cid, game)
            if source.controller.mana == 0: card.attack += 1; card.max_health += 2; card.health += 2
            game.current_player.add_to_hand(card)
        game.initiate_discover(source.controller, random.sample(demons, min(3, len(demons))), on_choose)
