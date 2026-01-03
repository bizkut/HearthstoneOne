"""
Meta Decks Collection for HearthstoneOne AI Training.

Contains real competitive deck codes from Standard and Wild formats.
Deck codes can be imported using the deck_parser module.
"""

# Standard Meta Decks (2024-2025 Season)
STANDARD_DECKS = {
    # Aggro/Tempo
    "pirate_warrior": "AAECAQcG15/FAouLBNm8BKvIBLPIBJ2lBgyhrQTdrQT+sAT9sASW1ASY1ASq2wTB5gTu5gTQigWeigbalAbdlQYA",
    "face_hunter": "AAECAR8G7qwE4c0EmNQE398E9aIF9bAFDIXsA/f4A8X7A/aOBNqfBMe5BOG6BP/OBJLlBMH5BPuKBev5BAAA",
    "aggro_paladin": "AAECAZ8FBPTOBPHQBNL/BOWgBQ3M6wOU7wON9AO+gwSRnQSloASvuwTIuwSnzgTDzwTc3wS02wWy3wUA",
    
    # Midrange/Control
    "dragon_priest": "AAECAa0GCOe0BNu0BIXsBI7yBJHQBf3bBY/eBfjeBQvipASDpQTtsQS3swStsgXkswWpzAWi8AWR+gWK/AXZhwYA",
    "control_warrior": "AAECAQcM+cIF474EhNkEit4E+eIEnewE8O4EiPcEj/gEtPUF4vYF3fYFCdrYBI7bBNbiBI/lBI/ZBf3bBf7bBaTdBaXdBY/eBQA=",
    "blood_dk": "AAECAeMVBobhBAv86QTo7ASJgQWz+gWS9QXn9QXv9gX49gWP+AWS+AWd+QWLhwYA",
    
    # Combo
    "mill_rogue": "AAECAaIHBobLBInuBM77BPCiBabpBfjrBQzl5ASt6gSh7gTN8ATH+QS4jQWfkQWdmgWsmQWl5gXI6wXL7AUA",
    "otk_mage": "AAECAf0ECJCS9g/E+A+PkBAHwqoT26sT4K0Ti64TnK4T3rgT+8ATAA==",
    
    # Value
    "ramp_druid": "AAECAbSkAwaIsgXRswW+tQXcsQXpsgX3sgUM7bEE4swE/dQE9K0F+a0F/rkFsr4Fsr8FtL8Fu8EFosIF8sIFAA==",
    "big_shaman": "AAECAaoIBPSmBKikBe+BBaacBg2q3gTb3wTB4gT++gT4+wTG/ASJgQWGhgWnjwXbkgXOmwX4ngW+nwUA",
}

# Wild Meta Decks (Eternal Format)
WILD_DECKS = {
    # Aggro/Tempo  
    "pirate_rogue_wild": "AAEBAaIHBKO0A/vEA8PhA/uKBAKgzQK09gMA",
    "secret_mage_wild": "AAEBAf0EAr+kA/usAwocSooBywTmBJYFvwi/rALF8wLBuAMAA",
    "odd_paladin_wild": "AAEBAZ8FBK8EpwWPggP7uAMNRsUD2f4CnvACvfMC48sDnuED0eEDmesDipsEq6AE57YE12EAAA==",
    
    # Combo
    "quest_mage_wild": "AAEBAf0EBv+kA/usA9DBBMfOBPP0BLj2BA7mBJYF7AeNCL+kA6GhBL7sBPfqBJ/kBNvqBOD2BIv3BOL3BPv4BAA=",
    "reno_priest_wild": "AAECAa0GHu0BwgS5BtMK1wrXCvoR0cEC6NACA6awA5mpA4GxA5G+A9jCA/vRA/jjA5LkA5nuA6HsA/LxA/7xA/70A722BJf2BI76BLT5BLr5BJiDBY2/Be7GBQAA",
    
    # Control
    "cube_lock_wild": "AAEBAf0GCPcE4QfhzAKX0wKS/gLFuQOvxQP0+QMQowHECMwIvhTnywKuzQKH0QK/8QKF+gKd+wK/8gOC+gOC+QSEjQWongWEswUA",
    "dead_mans_hand_warrior": "AAECAQcOkQb/DZAOoM0C8dMC8+cCm/MCkvgCkp8D0qUD/KMD3q0D/q4D/McGCRaQBagF+Af7D9/RAv7nAo77Ao7TAguS/wIA",
    
    # Aggro
    "mech_paladin_wild": "AAECAYsWAovhApH7Ag6xoQTdoQS3pgSvoASfoQSstwSHpgS2oQSKoQTWoAS6oQSUqQS5oQSnoQQA",
    "even_shaman_wild": "AAEBAaoICM/HAu+OA9ySA+G5A+XYBPj7BJj7BL36BAv2vQKN8gLv0gPbuAP8vAPlzAPw1AO7tgT21gTQ0gSBhAUA",
}

# Classic/Basic Fallback Decks (for testing)
BASIC_DECKS = {
    "basic_mage": [
        "CS2_023", "CS2_023",  # Arcane Intellect
        "CS2_024", "CS2_024",  # Frostbolt
        "CS2_025", "CS2_025",  # Arcane Explosion
        "CS2_026", "CS2_026",  # Frost Nova
        "CS2_027", "CS2_027",  # Mirror Image
        "CS2_029", "CS2_029",  # Fireball
        "CS2_032", "CS2_032",  # Flamestrike
        "CS2_182", "CS2_182",  # Chillwind Yeti
        "CS2_186", "CS2_186",  # War Golem
        "CS2_187", "CS2_187",  # Booty Bay Bodyguard
        "CS2_120", "CS2_120",  # River Crocolisk
        "CS2_121", "CS2_121",  # Frostwolf Grunt
        "CS2_189", "CS2_189",  # Elven Archer
        "CS2_200", "CS2_200",  # Boulderfist Ogre
        "EX1_015", "EX1_015",  # Novice Engineer
    ],
    "basic_warrior": [
        "CS2_103", "CS2_103",  # Charge
        "CS2_105", "CS2_105",  # Heroic Strike
        "CS2_106", "CS2_106",  # Fiery War Axe
        "CS2_108", "CS2_108",  # Execute
        "CS2_114", "CS2_114",  # Cleave
        "EX1_400", "EX1_400",  # Whirlwind
        "EX1_410", "EX1_410",  # Shield Slam
        "CS2_182", "CS2_182",  # Chillwind Yeti
        "CS2_186", "CS2_186",  # War Golem
        "CS2_187", "CS2_187",  # Booty Bay Bodyguard
        "CS2_120", "CS2_120",  # River Crocolisk
        "CS2_121", "CS2_121",  # Frostwolf Grunt
        "CS2_200", "CS2_200",  # Boulderfist Ogre
        "EX1_029", "EX1_029",  # Leper Gnome
        "EX1_015", "EX1_015",  # Novice Engineer
    ],
}

def get_random_deck_pair():
    """Get a random pair of decks for training (deckcode strings)."""
    import random
    all_decks = list(STANDARD_DECKS.values()) + list(WILD_DECKS.values())
    return random.choice(all_decks), random.choice(all_decks)

def get_basic_deck_pair():
    """Get basic decks as card ID lists (fallback)."""
    return BASIC_DECKS["basic_mage"], BASIC_DECKS["basic_warrior"]
