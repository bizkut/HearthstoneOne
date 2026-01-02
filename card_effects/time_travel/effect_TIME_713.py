"""Effect for TIME_713 in TIME_TRAVEL"""


def battlecry(game, source, target):
    game.summon_token(game.get_opponent(source.controller), 'TIME_713t', -1)
