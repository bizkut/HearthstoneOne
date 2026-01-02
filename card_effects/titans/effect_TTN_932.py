"""Effect for TTN_932 in TITANS"""


def on_play(game, source, target):
    # Destroy a friendly minion to destroy an enemy minion.
    # Needs two targets... Hearthstone usually handles this as one manual target.
    # We'll assume target is the enemy minion.
    if target:
        target.destroy()
        # Find a random friendly minion to destroy
        import random
        friendlies = source.controller.board[:]
        if friendlies:
            random.choice(friendlies).destroy()
