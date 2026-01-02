"""Effect for CFM_621 in GANGS"""


def battlecry(game, source, target):
    player = source.controller
    ids = [c.card_id for c in player.deck]
    if len(ids) == len(set(ids)):
        # Kazakus: Get random potion
        player.add_to_hand(create_card('CFM_621t', game))
