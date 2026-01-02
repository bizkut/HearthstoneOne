"""Effect for TIME_713t in TIME_TRAVEL"""


def deathrattle(game, source):
    for _ in range(5):
        game.get_opponent(source.controller).add_to_hand(create_card('GAME_005', game))
