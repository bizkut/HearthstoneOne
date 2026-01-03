"""Effect for CORE_RLK_121 in CORE"""
from simulator.enums import Race

def setup(game, source):
    def on_death(game, trig_src, minion):
        # Check if minion is Undead (use getattr for safety, compare to Race enum)
        minion_race = getattr(minion, 'race', None) or getattr(getattr(minion, 'data', None), 'race', None)
        if minion.controller == trig_src.controller and minion_race == Race.UNDEAD:
            trig_src.controller.draw(1)
    game.register_trigger('on_minion_death', source, on_death)