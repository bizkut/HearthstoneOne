"""Effect for VAC_341 in ISLAND_VACATION"""


def battlecry(game, source, target):
    if target and target.attack <= source.attack:
        target.destroy()
