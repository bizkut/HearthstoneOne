"""Effect for VAN_CS2_027 in VANILLA"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'CS2_027t', source.zone_position)
    game.summon_token(source.controller, 'CS2_027t', source.zone_position)