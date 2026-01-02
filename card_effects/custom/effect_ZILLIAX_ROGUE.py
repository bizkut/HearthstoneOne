"""Effect for ZILLIAX_ROGUE in CUSTOM"""


def setup(game, source):
    # Set stats and cost (simulating the build)
    # This setup is called when card effect is loaded, but stats are usually static data.
    # However, we can modify the entity in setup/battlecry.
    # Ideally should be done in __init__ but we don't control that easily without data patch.
    # We will patch data below in the main function.
    
    # Keywords
    source.divine_shield = True
    source.taunt = True
    source.lifesteal = True
    source.rush = True
    
    # Haywire effect
    def on_end(game, trig_src, *args):
        if game.current_player == trig_src.controller:
            game.deal_damage(trig_src.controller.hero, 3, source)
    game.register_trigger('on_turn_end', source, on_end)
