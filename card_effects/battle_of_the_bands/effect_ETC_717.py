"""Effect for ETC_717 in BATTLE_OF_THE_BANDS"""

def on_play(game, source, target):
    if source.controller.hero.weapon: source.controller.hero.weapon.attack += 3