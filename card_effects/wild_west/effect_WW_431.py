"""Effect for WW_431 in WILD_WEST"""

def setup(game, source):
    def on_end(game, trig_src, *args):
        if game.current_player == trig_src.controller:
            # Effect placeholder
            pass
    game.register_trigger('on_turn_end', source, on_end)