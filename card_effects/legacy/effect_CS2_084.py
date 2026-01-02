"""Effect for CS2_084 in LEGACY"""

def on_play(game, source, target):
    import random
    targets = source.controller.opponent.board[:]
    if targets:
        for _ in range(2): game.deal_damage(random.choice(targets), 2, source)