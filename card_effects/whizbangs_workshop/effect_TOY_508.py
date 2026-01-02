"""Effect for TOY_508 in WHIZBANGS_WORKSHOP"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'WW_010hexfrog', source.zone_position + 1)
    game.summon_token(source.controller, 'WW_010hexfrog', source.zone_position + 2)
