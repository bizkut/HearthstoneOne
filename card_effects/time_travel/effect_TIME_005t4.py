"""Effect for TIME_005t4 in TIME_TRAVEL"""


def battlecry(game, source, target):
    p = source.controller
    armor = 5
    if any(c.card_id.startswith('TIME_005') for c in p.hand if c != source):
        armor += 5
    p.gain_armor(armor)
