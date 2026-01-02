"""Effect for TIME_024 in TIME_TRAVEL"""


def battlecry(game, source, target):
    def on_start(game, trig_src, *args):
        if game.current_player == trig_src.controller:
            trig_src.attack = 99 # Infinity!
    game.register_trigger('on_turn_start', source, on_start)
