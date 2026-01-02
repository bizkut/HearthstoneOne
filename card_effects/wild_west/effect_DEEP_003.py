"""Effect for DEEP_003 in WILD_WEST"""


def on_play(game, source, target):
    if target: 
        game.deal_damage(target, 1, source)
        from simulator.card_loader import CardDatabase
        import random
        # Summon random minion of that cost (1)
        options = [c.card_id for c in CardDatabase.get_collectible_cards() if c.cost == 1 and c.card_type == CardType.MINION]
        if options: source.controller.summon(create_card(random.choice(options), game))
