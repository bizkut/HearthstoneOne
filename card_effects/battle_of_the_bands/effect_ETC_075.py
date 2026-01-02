"""Effect for ETC_075 in BATTLE_OF_THE_BANDS"""


def on_play(game, source, target):
    source.controller.draw(2)
    if source.controller.mana == 0: # Finale
        if source.controller.hero.weapon:
            source.controller.hero.weapon.attack += 2
