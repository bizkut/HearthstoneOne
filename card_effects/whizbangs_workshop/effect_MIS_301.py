"""Effect for MIS_301 in WHIZBANGS_WORKSHOP"""


def on_play(game, source, target):
    game.summon_token(source.controller, 'EX1_158t', source.zone_position + 1)
    treants = [m for m in source.controller.board if 'Treant' in m.name]
    source.controller.draw(len(treants))
