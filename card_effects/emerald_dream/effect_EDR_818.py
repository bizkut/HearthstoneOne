"""Effect for EDR_818 in EMERALD_DREAM"""

def setup(game, source):
    def on_start(game, trig_src, *args):
        if game.current_player == trig_src.controller:
            # Effect placeholder
            pass
    game.register_trigger('on_turn_start', source, on_start)