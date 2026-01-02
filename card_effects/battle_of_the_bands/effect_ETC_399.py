"""Effect for ETC_399 in BATTLE_OF_THE_BANDS"""


def setup(game, source):
    def on_atk(game, trig_src, target):
        if trig_src.controller == source.controller and trig_src.rush:
            for m in source.controller.board: m.attack += 1
    game.register_trigger('on_attack', source, on_atk)
