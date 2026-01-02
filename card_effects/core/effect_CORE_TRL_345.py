"""Effect for CORE_TRL_345 in CORE"""

def battlecry(game, source, target):
    for cid in source.controller.spells_played_this_game:
         source.controller.add_to_hand(create_card(cid, game))