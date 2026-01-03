from typing import Dict

def get_class_index(hero_id: str) -> int:
    """
    Map hero ID to class index consistently across the project.
    
    Args:
        hero_id: Card ID of the hero (e.g., "HERO_01")
        
    Returns:
        Class index (0-10) or 0 if unknown.
    """
    class_map = {
        "HERO_01": 0,  # Warrior
        "HERO_02": 1,  # Shaman
        "HERO_03": 2,  # Rogue
        "HERO_04": 3,  # Paladin
        "HERO_05": 4,  # Hunter
        "HERO_06": 5,  # Druid
        "HERO_07": 6,  # Warlock
        "HERO_08": 7,  # Mage
        "HERO_09": 8,  # Priest
        "HERO_10": 9,  # Death Knight
        "HERO_11": 10, # Demon Hunter
    }
    # Handle skins or variations if they preserve the prefix (simplified)
    # Ideally should use CardDatabase to get class, but this is fast for standard IDs
    return class_map.get(hero_id[:7], 0)
