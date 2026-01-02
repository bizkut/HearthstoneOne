"""Effect for DEEP_016 in WILD_WEST"""


def setup(game, source):
    source.lifesteal = True
    def on_dmg(game, trig_src, target, amount, dmg_src):
        if dmg_src == source.controller.hero:
            target.frozen = True
    game.register_trigger('on_damage_taken', source, on_dmg)
