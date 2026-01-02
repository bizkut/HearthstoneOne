"""Effect for ULD_156 in ULDUM"""

def battlecry(game, source, target):
    player = source.controller
    ids = [c.card_id for c in player.deck]
    if len(ids) == len(set(ids)):
        # Effect here - needs manual adjustment for specific card
        pass