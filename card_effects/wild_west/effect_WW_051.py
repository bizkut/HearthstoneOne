"""Effect for WW_051 in WILD_WEST"""


def on_play(game, source, target):
    for p in game.players:
        for i in range(3):
            m = create_card('WW_051t', game)
            if p == source.controller: m.rush = True
            p.summon(m)
