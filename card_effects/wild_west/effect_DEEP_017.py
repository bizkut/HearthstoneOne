"""Effect for DEEP_017 in WILD_WEST"""


def on_play(game, source, target):
    for _ in range(2):
        game.summon_token(source.controller, 'CS2_101t', source.zone_position + 1)
