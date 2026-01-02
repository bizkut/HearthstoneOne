"""Effect for VAN_CS2_026 in VANILLA"""

def on_play(game, source, target):
    for m in source.controller.opponent.board[:]: m.frozen = True