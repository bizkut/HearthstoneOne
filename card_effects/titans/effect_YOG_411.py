"""Effect for YOG_411 in TITANS"""


def battlecry(game, source, target):
    if len(source.controller.spells_played_this_game) >= 5:
        opp = source.controller.opponent
        game.deal_damage(opp.hero, 2, source)
        for m in opp.board[:]:
            game.deal_damage(m, 2, source)
