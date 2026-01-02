"""Effect for CORE_EX1_016 in CORE"""


def setup(game, source):
    def on_summon(game, trig_src, minion):
        if minion.controller == trig_src.controller and minion != trig_src:
            import random
            opp = trig_src.controller.opponent
            t = random.choice([opp.hero] + opp.board)
            game.deal_damage(t, 1, trig_src)
    game.register_trigger('on_minion_summon', source, on_summon)
