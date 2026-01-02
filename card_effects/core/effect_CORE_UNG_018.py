"""Effect for CORE_UNG_018 in CORE"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)
    source.controller.add_to_hand(create_card('UNG_809t', game))