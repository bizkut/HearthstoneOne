"""Effect for TOY_520 in WHIZBANGS_WORKSHOP"""

def setup(game, source):
    def on_start(game, trig_src, *args):
        if game.current_player == trig_src.controller:
            # Effect placeholder
            pass
    game.register_trigger('on_turn_start', source, on_start)