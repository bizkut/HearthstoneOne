"""Effect for VAN_EX1_298 in VANILLA"""


def setup(game, source):
    source.cant_attack = True
    def on_end(game, trig_src):
        if game.current_player == trig_src.controller:
            opp = game.get_opponent(trig_src.controller).board + [game.get_opponent(trig_src.controller).hero]
            import random
            game.deal_damage(random.choice(opp), 8, source)
    game.register_trigger('on_turn_end', source, on_end)
