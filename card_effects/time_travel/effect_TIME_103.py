"""Effect for TIME_103 in TIME_TRAVEL"""
from simulator.card_loader import create_card

def deathrattle(game, source):
    # Draw copies of cards played this game
    played = list(source.controller.cards_played_this_game)
    for cid in played[-3:]: # Draw last 3 for balance
         source.controller.add_to_hand(create_card(cid, game))
