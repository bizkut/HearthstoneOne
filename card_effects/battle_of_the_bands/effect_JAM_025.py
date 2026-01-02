"""Effect for JAM_025 in BATTLE_OF_THE_BANDS"""


def on_play(game, source, target):
    if target: 
        game.heal(target, 3)
        # Check neighbors
        pos = target.zone_position
        board = target.controller.board
        for m in board:
            if m.zone_position in [pos - 1, pos + 1]:
                 game.heal(m, 3)
