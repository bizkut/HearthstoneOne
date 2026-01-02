"""Effect for TTN_927 in TITANS"""


def battlecry(game, source, target):
    if target and 'Treant' in target.name:
        target.transform('TTN_927t') # 5/5 Ancient with Taunt
