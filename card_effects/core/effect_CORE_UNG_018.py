"""Effect for CORE_UNG_018 in CORE"""
from simulator.card_loader import create_card

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)
    card = create_card('UNG_809t', game)
    if card:
        source.controller.add_to_hand(card)