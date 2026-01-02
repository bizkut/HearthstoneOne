"""Effect for MIS_714 in WHIZBANGS_WORKSHOP"""


def on_play(game, source, target):
    if target:
        copy = create_card(target.card_id, game)
        if source.controller.summon(copy):
             game.attack(copy, target)
