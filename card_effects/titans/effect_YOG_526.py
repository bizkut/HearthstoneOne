"""Effect for YOG_526 in TITANS"""


def on_play(game, source, target):
    if target: game.deal_damage(target, 3, source)
    # Combo simplified to always trigger for now or check turn history
    if source.controller.cards_played_this_turn:
        source.controller.add_to_hand(create_card('YOG_514t', game))
