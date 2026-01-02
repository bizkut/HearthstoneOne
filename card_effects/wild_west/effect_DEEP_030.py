"""Effect for DEEP_030 in WILD_WEST"""


def setup(game, source):
    source.battlecry = lambda g, s, t: (s.controller.draw(1), game.deal_damage(s.controller.hero, 2, s))
    source.deathrattle = lambda g, s: (s.controller.draw(1), game.deal_damage(s.controller.hero, 2, s))
