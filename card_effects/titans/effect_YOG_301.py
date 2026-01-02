"""Effect for YOG_301 in TITANS"""


def on_play(game, source, target):
    for p in game.players:
        p.fatigue += 1
        game.deal_damage(p.hero, p.fatigue, source)
        p.fatigue += 1
        game.deal_damage(p.hero, p.fatigue, source)
