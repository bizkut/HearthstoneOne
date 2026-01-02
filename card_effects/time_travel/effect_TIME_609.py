"""Effect for TIME_609 in TIME_TRAVEL"""


def battlecry(game, source, target):
    # Deal 2 damage to all enemies, repeat logic simplified
    repeats = 1
    # Check for sisters in history
    played = [c.name for c in source.controller.cards_played_this_game]
    if 'Alleria' in played: repeats += 1
    if 'Vereesa' in played: repeats += 1
    for _ in range(repeats):
        for m in game.get_opponent(source.controller).board[:] + [game.get_opponent(source.controller).hero]:
            game.deal_damage(m, 2, source)
