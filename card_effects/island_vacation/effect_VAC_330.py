"""Effect for VAC_330 in ISLAND_VACATION"""

def deathrattle(game, source):
    source.controller.add_to_hand(create_card('GAME_005', game))