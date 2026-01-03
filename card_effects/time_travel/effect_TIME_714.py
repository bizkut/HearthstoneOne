"""Effect for TIME_714 in TIME_TRAVEL"""


def battlecry(game, source, target):
    # Destroy minions played last turn
    history = getattr(source.controller.opponent, 'cards_played_last_turn', [])
    if not isinstance(history, (list, set, tuple)):
        history = []
    history_ids = [c.card_id if hasattr(c, 'card_id') else c for c in history]
    for m in source.controller.opponent.board[:]:
        if m.card_id in history_ids:
            m.destroy()
