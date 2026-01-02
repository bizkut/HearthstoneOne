"""Effect for TIME_435 in TIME_TRAVEL"""


def battlecry(game, source, target):
    if target and target.health <= source.health:
        # Steal minion
        target.controller.board.remove(target)
        source.controller.board.append(target)
        target.controller = source.controller
