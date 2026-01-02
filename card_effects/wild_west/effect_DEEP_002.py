"""Effect for DEEP_002 in WILD_WEST"""


def on_play(game, source, target):
    import random
    cid = random.choice(['DEEP_002t', 'DEEP_002t2', 'DEEP_002t3'])
    source.controller.summon(create_card(cid, game))
