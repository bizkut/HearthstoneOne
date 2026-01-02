"""Effect for MIS_307 in WHIZBANGS_WORKSHOP"""


def battlecry(game, source, target):
    tinyfin = create_card('CS2_168', game)
    tinyfin.attack = source.attack
    tinyfin.max_health = source.health
    tinyfin.health = source.health
    tinyfin.rush = True
    source.controller.summon(tinyfin, source.zone_position + 1)
