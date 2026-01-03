"""Effect for CORE_RLK_121 in CORE"""
from simulator.enums import Race

def setup(game, source):
    def on_death(game, trig_src, minion):
        if minion.controller == trig_src.controller and Race.UNDEAD in getattr(minion, 'races', []):
            trig_src.controller.draw(1)
    game.register_trigger('on_minion_death', source, on_death)