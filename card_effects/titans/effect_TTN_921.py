"""Effect for TTN_921 in TITANS"""


def setup(game, source):
    def on_atk(game, trig_src, target):
        if trig_src == source:
            source.controller.add_to_hand(create_card('GAME_005', game))
    game.register_trigger('on_attack', source, on_atk)
