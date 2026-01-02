"""Effect for WW_044 in WILD_WEST"""

def deathrattle(game, source):
    source.controller.add_to_hand(create_card('WW_041t', game))