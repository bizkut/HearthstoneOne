"""Effect for TIME_209 in TIME_TRAVEL"""


def battlecry(game, source, target):
    player = source.controller
    # Search for High King's Hammer in deck or hand
    hammer = next((c for c in player.deck if c.card_id == 'TIME_209t'), None)
    if not hammer:
        hammer = next((c for c in player.hand if c.card_id == 'TIME_209t'), None)
    
    if hammer:
        if hammer in player.deck: player.deck.remove(hammer)
        elif hammer in player.hand: player.hand.remove(hammer)
        player.equip_weapon(hammer)
    else:
        # If not found, create a new one? (Safeguard)
        player.equip_weapon(create_card('TIME_209t', game))

def deathrattle(game, source):
    source.controller.add_to_hand(create_card('TIME_209t', game))
