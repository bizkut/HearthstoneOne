"""Effect for ULD_003 in ULDUM"""


def battlecry(game, source, target):
    player = source.controller
    ids = [c.card_id for c in player.deck]
    if len(ids) == len(set(ids)):
        # Zephrys: Give a "Perfect" card (simplified: draw a strong card)
        player.draw(1)
