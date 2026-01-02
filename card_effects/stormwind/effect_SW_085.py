"""Effect for SW_085 in STORMWIND"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'SW_085t', source.zone_position + 1)
