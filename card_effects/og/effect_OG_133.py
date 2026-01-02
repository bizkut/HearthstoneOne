"""Effect for OG_133 in OG"""


def battlecry(game, source, target):
    # Yogg-Saron: Cast random spells for each spell cast
    count = source.controller.spells_played_this_game_count
    from simulator.card_loader import CardDatabase
    import random
    spells = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.SPELL]
    for _ in range(count):
        if not spells: break
        sid = random.choice(spells)
        # Simplified: cast at random target
        game.play_card(create_card(sid, game))
