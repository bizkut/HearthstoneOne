"""Effect for EX1_007 in EXPERT1"""

def setup(game, source):
    def on_dmg(game, trig_src, target, dmg, damager):
        if target == trig_src: trig_src.controller.draw(1)
    game.register_trigger('on_damage_taken', source, on_dmg)