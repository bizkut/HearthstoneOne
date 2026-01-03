"""Effect for EX1_575 in EXPERT1"""

def setup(game, source):
    def on_end(game, trig_src, *args):
        if game.current_player == trig_src.controller:
            trig_src.controller.draw(1)
    game.register_trigger('on_turn_end', source, on_end)