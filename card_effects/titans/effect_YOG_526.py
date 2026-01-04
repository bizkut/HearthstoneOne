"""Effect for YOG_526 in TITANS"""

from simulator.card_loader import create_card


def on_play(game, source, target):
    if target:
        game.deal_damage(target, 3, source)
    # Combo: if played another card this turn, add a Coin to hand
    if source.controller.cards_played_this_turn:
        coin = create_card('YOG_514t', game)
        if coin:  # Guard against missing card data
            source.controller.add_to_hand(coin)

