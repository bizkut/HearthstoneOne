"""Effect for TIME_005t5 in TIME_TRAVEL"""


def battlecry(game, source, target):
    p = source.controller
    if any(c.card_id.startswith('TIME_005') for c in p.hand if c != source):
        p.summon(create_card(source.card_id, game))
