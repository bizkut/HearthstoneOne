import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator.card_loader import CardDatabase

def find_cards():
    db = CardDatabase.get_instance()
    db.load()
    
    decks = {
        "AGGRO_ROGUE": [
            "Preparation", "Shadowstep", "Deja Vu", "Nightmare Fuel", "Spacerock Collector",
            "Creature of Madness", "Flashback", "Foxy Fraud", "Oh, Manager!", 
            "Mirrex, the Crystalline", "Talgath", "Dubious Purchase", "Elise the Navigator",
            "Griftah, Trusted Vendor", "Nightmare Lord Xavius", "Scrapbooking Student",
            "Gnomelia, S.A.F.E. Pilot", "Zilliax Deluxe 3000", "Shaladrassil", "Ashamane"
        ],
        "PEDDLER_DH": [
            "First Portal to Argus", "Illidari Studies", "Red Card", "Tuskpiercer", "Broxigar",
            "Grim Harvest", "Infestation", "Axe of Cenarius", "Return Policy", "Wyvern's Slumber",
            "Dangerous Cliffside", "Elise the Navigator", "Nightmare Lord Xavius", 
            "Raging Felscreamer", "Window Shopper", "Spirit Peddler", "Chrono-Lord Deios",
            "Ferocious Felbat", "Perennial Serpent", "Zilliax Deluxe 3000", "Fyrakk the Blazing"
        ],
        "CONTROL_DK": [
            "Morbid Swarm", "Creature of Madness", "Dreadhound Handler", "Infested Breath",
            "Chillfallen Baron", "Blob of Tar", "Elise the Navigator", "Griftah, Trusted Vendor",
            "Nightmare Lord Xavius", "Corpse Explosion", "Foamrender", "Reanimated Pterrordax",
            "Sanguine Infestation", "Exarch Maladaar", "Hideous Husk", "Marin the Manager",
            "Shaladrassil", "Stitched Giant", "Ysera, Emerald Aspect", "Zilliax Deluxe 3000",
            "The Ceaseless Expanse"
        ]
    }
    
    for deck_name, card_names in decks.items():
        print(f"\n{deck_name} = [")
        for name in card_names:
            # Find card by name
            # Handle duplicates/ambiguities if needed, but taking first Exact match or first Contains match
            found = None
            
            # Exact match first
            for card in db._cards.values():
                if card.name.lower() == name.lower() and card.collectible:
                    found = card
                    break
            
            if not found:
                print(f"    # WARNING: Could not find exact match for '{name}'")
                # Try partial?
                # for card in db._cards.values():
                #     if name.lower() in card.name.lower() and card.collectible:
                #         found = card
                #         break
            
            if found:
                # Need to handle counts? The user provided counts (2x, 1x). 
                # This script just finds IDs. I will manually add counts when constructing the list.
                # Actually, self_play needs a list of identifiers (30 total).
                # I'll output the ID and name so I can construct the full list manually with counts.
                print(f"    '{found.card_id}', # {found.name}")
            else:
                 print(f"    'UNKNOWN', # {name}")
        print("]")

if __name__ == "__main__":
    find_cards()
