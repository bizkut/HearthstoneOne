"""Effect for CS2_114 in LEGACY"""

def on_play(game, source, target):
    import random
    opp_board = source.controller.opponent.board[:]
    if opp_board:
        targets = random.sample(opp_board, min(2, len(opp_board)))
        for t in targets: game.deal_damage(t, 2, source)