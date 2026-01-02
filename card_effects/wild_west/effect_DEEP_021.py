"""Effect for DEEP_021 in WILD_WEST"""


def on_play(game, source, target):
    if target:
        source.controller.add_to_hand(create_card(target.card_id, game))
        target.destroy()
