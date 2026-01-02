"""Effect for TIME_103 in TIME_TRAVEL"""


def deathrattle(game, source):
    # Draw copies of cards played this game
    played = [c for c in source.controller.cards_played_this_game]
    for cid in played[:3]: # Draw up to 3 for balance
         source.controller.add_to_hand(create_card(cid, game))
