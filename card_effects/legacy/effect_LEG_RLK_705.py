"""Effect for LEG_RLK_705 in LEGACY"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'RLK_060t', source.zone_position + 1)
    game.summon_token(source.controller, 'RLK_060t', source.zone_position + 2)
