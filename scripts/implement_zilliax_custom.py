import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator.card_loader import CardDatabase

def create_custom_zilliax_cards():
    """
    Creates virtual card entries for the specific Zilliax configurations
    used in the test decks. 
    """
    db = CardDatabase.get_instance()
    db.load()
    
    # 1. Zilliax Rogue (Haywire + Perfect)
    # Cost: 2 + 5 = 7
    # Stats: 4/4 + 3/2 = 7/6 (Note: Logic is Sum of stats? Or base? Zilliax base is 0/0/0 usually if modules purely add)
    # Base Zilliax TOY_330 is 0 cost? Let's check generally. 
    # Actually modules have cost. Zilliax cost = Sum of modules costs.
    # Stats = Sum of stats?
    # Let's assume sum.
    # Haywire (2/4/4) + Perfect (5/3/2) = 7 Mana, 7/6.
    # Keywords: Divine Shield, Taunt, Lifesteal, Rush.
    # Effect: End of turn deal 3 dmg to hero.
    
    # We will register this as a new card ID in the database dynamically (or better, make a dedicated Zilliax factory)
    # For now, let's just make a script that registers the effect for specific IDs we will use in the decks.
    # We'll use IDs: "ZILLIAX_ROGUE", "ZILLIAX_DH", "ZILLIAX_DK"
    
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    # ZILLIAX_ROGUE
    code_rogue = """
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
"""
    gen.implement_manually("ZILLIAX_ROGUE", code_rogue, "CUSTOM")

    # ZILLIAX_DH & DK (Twin + Perfect)
    # Twin (4/3/3) + Perfect (5/3/2) = 9 Mana, 6/5.
    # Keywords: Divine Shield, Taunt, Lifesteal, Rush, Battlecry: Copy.
    code_twin_perfect = """
def battlecry(game, source, target):
    # Twin Module: Summon a copy
    # We summon a copy of THIS minion (with current stats/buffs usually? or base copy?)
    # "Summon a copy of this" implies current state.
    game.summon_token(source.controller, source.card_id, source.zone_position + 1)
    # Since we are creating a custom card ID, summoning by ID works perfect as it has same stats.

def setup(game, source):
    source.divine_shield = True
    source.taunt = True
    source.lifesteal = True
    source.rush = True
"""
    gen.implement_manually("ZILLIAX_DH", code_twin_perfect, "CUSTOM")
    gen.implement_manually("ZILLIAX_DK", code_twin_perfect, "CUSTOM") # Same config
    
    print("Implemented Zilliax variants.")

def patch_database_for_zilliax():
    """Injects the custom Zilliax cards into the runtime database."""
    from simulator.entities import CardData, CardType, Race
    db = CardDatabase.get_instance()
    
    # Rogue: Haywire + Perfect
    rogue_z = CardData(
        card_id="ZILLIAX_ROGUE",
        name="Zilliax Deluxe 3000 (Rogue)",
        text="Divine Shield, Taunt, Lifesteal, Rush. End of turn: Deal 3 damage to your hero.",
        cost=7,
        attack=7,
        health=6,
        card_type=CardType.MINION,
        race=Race.MECHANICAL,
        rarity=5,
        card_set="CUSTOM",
        collectible=True
    )
    
    # DH/DK: Twin + Perfect
    dh_z = CardData(
        card_id="ZILLIAX_DH",
        name="Zilliax Deluxe 3000 (Twin/Perfect)",
        text="Divine Shield, Taunt, Lifesteal, Rush. Battlecry: Summon a copy of this.",
        cost=9,
        attack=6,
        health=5,
        card_type=CardType.MINION,
        race=Race.MECHANICAL,
        rarity=5,
        card_set="CUSTOM",
        collectible=True
    )
    
    # Add to DB
    db._cards["ZILLIAX_ROGUE"] = rogue_z
    db._cards["ZILLIAX_DH"] = dh_z
    db._cards["ZILLIAX_DK"] = dh_z # Reuse same data/logic
    
    print("Patched DB with Zilliax variants.")

if __name__ == "__main__":
    create_custom_zilliax_cards()
    # Note: Patching DB needs to happen in the main process, 
    # so we will call this function from self_play.py
