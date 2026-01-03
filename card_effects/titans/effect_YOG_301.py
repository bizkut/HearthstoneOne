"""Effect for YOG_301 in TITANS"""


def on_play(game, source, target):
    for p in game.players:
        # Access fatigue safely, default to 0 if not exists
        fatigue = getattr(p, 'fatigue', 0) + 1
        if hasattr(p, 'fatigue'):
            p.fatigue = fatigue
        if p.hero:
            game.deal_damage(p.hero, fatigue, source)
        fatigue += 1
        if hasattr(p, 'fatigue'):
            p.fatigue = fatigue
        if p.hero:
            game.deal_damage(p.hero, fatigue, source)
