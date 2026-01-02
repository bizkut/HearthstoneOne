"""Effect for ETC_073 in BATTLE_OF_THE_BANDS"""


def setup(game, source):
    count = source.controller.combo_cards_played = getattr(source.controller, 'combo_cards_played', 0)
    source.attack += count; source.max_health += count; source.health += count
