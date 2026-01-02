"""Effect for CS2_026 in LEGACY"""

def on_play(game, source, target):
    for m in source.controller.opponent.board[:]: m.frozen = True