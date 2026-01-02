"""Effect for TIME_618 in TIME_TRAVEL"""


def battlecry(game, source, target):
    p = source.controller
    # Death Knight mechanic: spend corpses to resurrect hero
    def on_hero_death(game, hero):
        if hero.controller == p and getattr(p, 'corpses', 0) > 0:
            spent = min(20, p.corpses)
            p.corpses -= spent
            hero.health = spent
            # Cancel death logic would be needed in engine, simplified fix:
            return True # Cancel death
    game.register_trigger('on_hero_death', source, on_hero_death)
