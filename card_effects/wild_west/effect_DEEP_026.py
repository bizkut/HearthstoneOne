from simulator.enums import CardType
"""Effect for DEEP_026 in WILD_WEST"""


def on_play(game, source, target):
    player = source.controller
    minions = [c.card_id for c in player.deck if c.card_type == CardType.MINION]
    if minions:
        import random
        chosen = random.sample(minions, min(3, len(minions)))
        def on_choose(game, cid):
            card = next((c for c in game.current_player.deck if c.card_id == cid), None)
            if card:
                game.current_player.draw_specific_card(card)
                game.current_player.hero.health += card.cost
        game.initiate_discover(player, chosen, on_choose)
