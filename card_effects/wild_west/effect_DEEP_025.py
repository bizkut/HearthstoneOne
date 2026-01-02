"""Effect for DEEP_025 in WILD_WEST"""


def on_play(game, source, target):
    if target:
        source.controller.add_to_hand(create_card(target.card_id, game))
        source.controller.add_to_deck(create_card(target.card_id, game))
        source.controller.summon(create_card(target.card_id, game))
