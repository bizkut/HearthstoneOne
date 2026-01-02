"""Effect for ZILLIAX_DK in CUSTOM"""


def battlecry(game, source, target):
    # Twin Module: Summon a copy
    # We summon a copy of THIS minion (with current stats/buffs usually? or base copy?)
    # "Summon a copy of this" implies current state.
    game.summon_token(source.controller, source.card_id, source.zone_position + 1)
    # Since we are creating a custom card ID, summoning by ID works perfect as it has same stats.

def setup(game, source):
    source.divine_shield = True
    source.taunt = True
    source.lifesteal = True
    source.rush = True
