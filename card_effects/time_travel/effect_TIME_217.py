"""Effect for TIME_217 in TIME_TRAVEL"""


def setup(game, source):
    def on_dmg(game, trig_src, target, amount, dmg_src):
        if target == trig_src and getattr(dmg_src, 'spell_school', None) == 'NATURE':
            # Summon 5-cost instead of damage (simplified fix)
            source.controller.summon(create_card('CS2_182', game)) # Boulderfist Ogre placeholder
    game.register_trigger('on_damage_taken', source, on_dmg)
