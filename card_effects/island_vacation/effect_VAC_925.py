"""Effect for VAC_925 in ISLAND_VACATION"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'TB_015', source.zone_position + 1)
    game.summon_token(source.controller, 'TB_015', source.zone_position + 2)
