"""Effect for JAM_022 in BATTLE_OF_THE_BANDS"""


def on_play(game, source, target):
    if target:
        target.silence()
        if source.controller.cards_played_this_turn:
            game.deal_damage(target, 2, source)
