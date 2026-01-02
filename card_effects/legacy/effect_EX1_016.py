"""Effect for EX1_016 in LEGACY"""


def deathrattle(game, source):
    opp_board = game.get_opponent(source.controller).board[:]
    if opp_board:
        import random
        target = random.choice(opp_board)
        # Steal target
        target.controller.board.remove(target)
        source.controller.board.append(target)
        target.controller = source.controller
