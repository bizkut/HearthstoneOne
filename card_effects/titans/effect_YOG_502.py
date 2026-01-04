"""Effect for YOG_502 in TITANS"""


def on_play(game, source, target):
    dmg = source.controller.armor
    for p in game.players:
        for m in p.board[:]:
            game.deal_damage(m, dmg, source)
