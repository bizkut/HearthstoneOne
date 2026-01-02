"""Effect for ETC_318 in BATTLE_OF_THE_BANDS"""


def on_play(game, source, target):
     p = source.controller
     count = 2
     if p.mana == 0: count = 3
     for _ in range(count):
         c = next((x for x in p.deck if x.cost == 1), None)
         if c: p.draw_specific_card(c); p.summon(c)
