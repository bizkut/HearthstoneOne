"""Effect for MIS_302 in WHIZBANGS_WORKSHOP"""


def on_play(game, source, target):
    if target:
        target.frozen = True
        copy = create_card(target.card_id, game)
        if source.controller.summon(copy):
            copy.frozen = True
