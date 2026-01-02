"""Effect for EDR_942 in EMERALD_DREAM"""

def setup(game, source):
    def on_end(game, trig_src, *args):
        if game.current_player == trig_src.controller:
            # Effect placeholder
            pass
    game.register_trigger('on_turn_end', source, on_end)