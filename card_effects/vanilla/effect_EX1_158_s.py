"""Effect for EX1_158_s in VANILLA"""

def on_play(game, source, target):
    for m in source.controller.board: game.register_trigger('on_death', m, lambda g, s, min: g.summon_token(min.controller, 'EX1_158t', min.zone_position))