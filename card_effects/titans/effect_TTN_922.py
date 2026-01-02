"""Effect for TTN_922 in TITANS"""


def on_play(game, source, target):
    player = source.controller
    # Shuffle the two left-most cards
    for _ in range(min(2, len(player.hand))):
        c = player.hand.pop(0)
        player.add_to_deck(c)
    player.shuffle_deck()
    player.draw(3)
