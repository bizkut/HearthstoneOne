"""Effect for EX1_612_bc in VANILLA"""

def battlecry(game, source, target):
    source.controller.next_secret_cost_0 = True