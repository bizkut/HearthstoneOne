"""Effect for SW_030 in STORMWIND"""

def setup(game, source):
    def on_end(game, trig_src, *args):
        if game.current_player == trig_src.controller:
            trig_src.controller.hero.gain_armor(3)
    game.register_trigger('on_turn_end', source, on_end)