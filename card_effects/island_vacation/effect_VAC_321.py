"""Effect for VAC_321 in ISLAND_VACATION"""

def setup(game, source):
    def on_end(game, trig_src, *args):
        if game.current_player == trig_src.controller:
            # Effect placeholder
            pass
    game.register_trigger('on_turn_end', source, on_end)