"""Effect for TIME_005t6 in TIME_TRAVEL"""


def battlecry(game, source, target):
    for m in game.current_player.board[:] + game.current_player.opponent.board[:]:
        if not m.card_id.startswith('TIME_005'):
            game.deal_damage(m, 6, source)
