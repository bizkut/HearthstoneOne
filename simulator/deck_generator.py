import random
from typing import List, Dict
from .card_loader import CardDatabase, CardClass, CardType

class DeckGenerator:
    """Helper class to generate decks for testing and self-play."""
    
    @staticmethod
    def get_random_deck(player_class: str = "MAGE", size: int = 30) -> List[str]:
        """Generate a random valid deck for a class."""
        db = CardDatabase.get_instance()
        if not db._loaded:
            db.load()
            
        # Get all valid cards for this class + Neutral
        valid_cards = []
        for card in db._cards.values():
            if not card.collectible:
                continue
            if card.card_type == CardType.HERO: # Don't put hero cards in deck for now
                continue
            
            is_class = str(card.card_class).upper() == player_class.upper()
            is_neutral = str(card.card_class) == "CardClass.NEUTRAL" or str(card.card_class) == "NEUTRAL"
            
            if is_class or is_neutral:
                valid_cards.append(card.card_id)
        
        # Prioritize Time Travel cards !
        timeways = [cid for cid in valid_cards if "TIME" in cid]
        others = [cid for cid in valid_cards if "TIME" not in cid]
        
        deck = []
        
        # Add some Timeways flavor
        deck.extend(random.choices(timeways, k=min(10, len(timeways))))
        
        # Fill the rest
        remaining = size - len(deck)
        if remaining > 0:
            deck.extend(random.choices(valid_cards, k=remaining))
            
        random.shuffle(deck)
        return deck[:size]

    @staticmethod
    def get_preset_deck(archetype: str) -> List[str]:
        """Get a predefined iconic deck."""
        
        if archetype == "AGGRO_ROGUE":
            deck = []
            deck.extend(["CORE_EX1_145"] * 2) # Preparation
            deck.extend(["CORE_EX1_144"] * 2) # Shadowstep
            deck.extend(["TIME_039"] * 2) # Deja Vu
            deck.extend(["EDR_528"] * 2) # Nightmare Fuel
            deck.extend(["GDB_875"] * 2) # Spacerock Collector
            deck.extend(["EDR_105"] * 2) # Creature of Madness
            deck.extend(["TIME_711"] * 2) # Flashback
            deck.extend(["CORE_DMF_511"] * 2) # Foxy Fraud
            deck.extend(["VAC_460"] * 2) # Oh, Manager!
            deck.append("DINO_407") # Mirrex
            deck.append("GDB_472") # Talgath
            deck.extend(["MIS_903"] * 2) # Dubious Purchase
            deck.append("TLC_100") # Elise
            deck.append("VAC_959") # Griftah
            deck.append("EDR_856") # Xavius
            deck.append("VAC_529") # Scrapbooking Student
            deck.append("CORE_TOY_100") # Gnomelia
            deck.append("ZILLIAX_ROGUE") # Zilliax (Haywire+Perfect)
            deck.append("EDR_846") # Shaladrassil
            deck.append("EDR_527") # Ashamane
            return deck

        elif archetype == "PEDDLER_DH":
            deck = []
            deck.append("TIME_039") # First Portal Placeholder (Deja Vu)
            deck.append("CORE_YOP_001") # Illidari Studies
            deck.extend(["TOY_644"] * 2) # Red Card
            deck.extend(["BAR_330"] * 2) # Tuskpiercer
            deck.append("TIME_020") # Broxigar
            deck.extend(["EDR_840"] * 2) # Grim Harvest
            deck.extend(["TLC_902"] * 2) # Infestation
            deck.append("CS2_106") # Axe of Cenarius Placeholder
            deck.extend(["MIS_102"] * 2) # Return Policy
            deck.extend(["EDR_820"] * 2) # Wyvern's Slumber
            deck.append("VAC_929") # Dangerous Cliffside
            deck.append("TLC_100") # Elise
            deck.append("EDR_856") # Xavius
            deck.extend(["BT_416"] * 2) # Raging Felscreamer
            deck.extend(["TOY_652"] * 2) # Window Shopper
            deck.extend(["WORK_015"] * 2) # Spirit Peddler
            deck.append("TIME_064") # Deios
            deck.append("EDR_892") # Felbat
            deck.append("TIME_022") # Perennial Serpent
            deck.append("ZILLIAX_DH") # Zilliax (Twin+Perfect)
            deck.append("FIR_959") # Fyrakk
            return deck

        elif archetype == "CONTROL_DK":
            deck = []
            deck.extend(["EDR_813"] * 2) # Morbid Swarm
            deck.extend(["EDR_105"] * 2) # Creature of Madness
            deck.extend(["VAC_514"] * 2) # Dreadhound Handler
            deck.extend(["EDR_814"] * 2) # Infested Breath
            deck.extend(["RLK_708"] * 2) # Chillfallen Baron
            deck.extend(["TLC_468"] * 2) # Blob of Tar
            deck.append("TLC_100") # Elise
            deck.append("VAC_959") # Griftah
            deck.append("EDR_856") # Xavius
            deck.append("CORE_RLK_035") # Corpse Explosion
            deck.append("MIS_101") # Foamrender
            deck.extend(["TLC_436"] * 2) # Reanimated Pterrordax
            deck.append("EDR_817") # Sanguine Infestation
            deck.append("GDB_470") # Maladaar
            deck.extend(["EDR_810"] * 2) # Hideous Husk
            deck.append("VAC_702") # Marin
            deck.append("EDR_846") # Shaladrassil
            deck.extend(["RLK_744"] * 2) # Stitched Giant
            deck.append("EDR_000") # Ysera
            deck.append("ZILLIAX_DK") # Zilliax (Twin+Perfect)
            deck.append("GDB_142") # Ceaseless Expanse
            return deck
            
        return DeckGenerator.get_random_deck()
