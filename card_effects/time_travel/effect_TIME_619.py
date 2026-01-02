"""Effect for TIME_619 in TIME_TRAVEL"""


def battlecry(game, source, target):
    p = source.controller
    bwonsamdi = next((c for c in p.deck + p.graveyard if 'Bwonsamdi' in c.name), None)
    if bwonsamdi:
        if bwonsamdi in p.deck: p.draw_specific_card(bwonsamdi)
        else: p.summon(bwonsamdi)
    else:
        p.add_to_hand(create_card('TRL_440', game)) # Bwonsamdi the Dead
