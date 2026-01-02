"""Effect for TIME_005t2 in TIME_TRAVEL"""


def battlecry(game, source, target):
    player = source.controller
    for c in player.hand:
        if c.card_id.startswith('TIME_005'):
            c.attack += 2; c.max_health += 2; c.health += 2
    for m in player.board:
        if m.card_id.startswith('TIME_005'):
            m.attack += 2; m.max_health += 2; m.health += 2
