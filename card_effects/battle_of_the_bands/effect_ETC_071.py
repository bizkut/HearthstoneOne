"""Effect for ETC_071 in BATTLE_OF_THE_BANDS"""


def deathrattle(game, source):
    for p in game.players:
        p.draw(2)
        # Discard 2 random
        import random
        for _ in range(min(2, len(p.hand))):
            p.hand.pop(random.randrange(len(p.hand)))
        # Destroy top 2
        p.deck = p.deck[2:]
