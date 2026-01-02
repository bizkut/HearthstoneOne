"""Effect for ETC_324 in BATTLE_OF_THE_BANDS"""


def setup(game, source):
    source.divine_shield = True
    def on_lose_ds(game, trig_src, target):
        if target.controller == source.controller:
            source.controller.draw(1)
    # Note: needs 'on_lose_divine_shield' event in engine
    game.register_trigger('on_damage_taken', source, lambda g, s, t, a, src: on_lose_ds(g, s, t))
