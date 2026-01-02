"""Effect for TIME_890 in TIME_TRAVEL"""


def battlecry(game, source, target):
    for m in game.current_player.board[:] + game.current_player.opponent.board[:]:
        if m != source:
            m.silence()
            m.destroy()
