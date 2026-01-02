"""Effect for TIME_714 in TIME_TRAVEL"""


def battlecry(game, source, target):
    # Destroy minions played last turn
    history = source.controller.opponent.cards_played_last_turn
    for m in source.controller.opponent.board[:]:
        if m.card_id in history:
            m.destroy()
