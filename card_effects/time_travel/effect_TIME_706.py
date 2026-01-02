"""Effect for TIME_706 in TIME_TRAVEL"""


def battlecry(game, source, target):
    p = source.controller
    old_hand = p.hand[:]
    import random
    p.hand = []
    for _ in range(3):
         if p.deck: p.draw()
    
    def on_end(game, trig_src, *args):
        trig_src.controller.hand = old_hand
    game.register_trigger('on_turn_end', source, on_end)
