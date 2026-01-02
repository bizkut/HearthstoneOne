"""Effect for CORE_UNG_809 in CORE"""

def battlecry(game, source, target):
    source.controller.add_to_hand(create_card('UNG_809t', game))