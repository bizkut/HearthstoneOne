"""Effect for DEEP_019 in WILD_WEST"""


def on_play(game, source, target):
    if target:
        copy = create_card(target.card_id, game)
        # Simplified: doesn't go dormant, just summons
        source.controller.summon(copy)
