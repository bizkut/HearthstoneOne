"""Effect for WW_0700 in WILD_WEST"""


def battlecry(game, source, target):
    p = source.controller
    ids = [c.card_id for c in p.deck]
    if len(ids) == len(set(ids)):
        for m in p.opponent.board[:]:
            m.destroy() # Poof!
