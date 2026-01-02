"""Effect for CORE_LOE_011 in CORE"""


def battlecry(game, source, target):
    p = source.controller
    ids = [c.card_id for c in p.deck]
    if len(ids) == len(set(ids)):
        p.hero.health = p.hero.max_health
