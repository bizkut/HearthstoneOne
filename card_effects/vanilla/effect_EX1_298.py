"""Effect for EX1_298 in VANILLA"""


def battlecry(game, source, target):
    # Ragnaros target selection? No, Ragnaros is end of turn.
    pass
def setup(game, source):
    def on_end(game, trig_src):
        if game.current_player == trig_src.controller:
            import random
            opp = trig_src.controller.opponent
            t = random.choice([opp.hero] + opp.board)
            game.deal_damage(t, 8, trig_src)
    game.register_trigger('on_turn_end', source, on_end)
