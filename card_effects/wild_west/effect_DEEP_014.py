"""Effect for DEEP_014 in WILD_WEST"""


def setup(game, source):
    def on_atk(game, trig_src, target):
        if trig_src == source.controller.hero:
            source.controller.draw(1)
    game.register_trigger('on_attack', source, on_atk)
