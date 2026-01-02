"""Effect for MIS_107 in WHIZBANGS_WORKSHOP"""


def on_play(game, source, target):
    dmg = 3
    if not any(c.card_type == CardType.MINION for c in source.controller.deck):
        dmg = 6
    for _ in range(dmg):
        opp = source.controller.opponent.board[:]
        if opp:
            import random
            game.deal_damage(random.choice(opp), 1, source)
