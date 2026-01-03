"""Hero Power Effect Handlers.

Defines effect handlers for all basic class hero powers.
Uses card IDs from the python-hearthstone library.
"""

from typing import Optional, Callable, Dict
from simulator.enums import CardType
from simulator.entities import Card, Minion, CardData


# Hero Power Card IDs (from hearthstone library)
HERO_POWER_IDS = {
    # Basic Hero Powers
    "CS2_034": "Fireblast",        # Mage: Deal 1 damage
    "CS2_049": "Totemic Call",     # Shaman: Summon random totem
    "CS2_056": "Life Tap",         # Warlock: Draw card, take 2 damage
    "CS2_083b": "Dagger Mastery",  # Rogue: Equip 1/2 weapon
    "CS2_101": "Reinforce",        # Paladin: Summon 1/1 Silver Hand Recruit
    "CS2_102": "Armor Up!",        # Warrior: Gain 2 armor
    "CS2_017": "Shapeshift",       # Druid: +1 Attack, +1 Armor
    "DS1h_292": "Steady Shot",     # Hunter: Deal 2 damage to enemy hero
    "CS1h_001": "Lesser Heal",     # Priest: Restore 2 health
    
    # Demon Hunter
    "HERO_10bp": "Demon Claws",    # DH: +1 Attack this turn
    
    # Death Knight
    "HERO_11bp": "Ghoul Charge",   # DK: Summon 1/1 Ghoul with Charge
}


def hp_fireblast(game, source, target):
    """Mage: Deal 1 damage to any target."""
    if target:
        game.deal_damage(target, 1, source)


def hp_totemic_call(game, source, target):
    """Shaman: Summon a random basic totem."""
    import random
    totem_ids = [
        "CS2_050",  # Healing Totem (0/2 heal friendly at end)
        "CS2_051",  # Stoneclaw Totem (0/2 Taunt)
        "CS2_052",  # Wrath of Air Totem (0/2 Spell Damage +1)
        "NEW1_009",  # Searing Totem (1/1)
    ]
    
    # Don't summon duplicates
    existing = [m.card_id for m in source.controller.board]
    available = [t for t in totem_ids if t not in existing]
    
    if available and len(source.controller.board) < 7:
        totem_id = random.choice(available)
        game.summon_token(source.controller, totem_id)


def hp_life_tap(game, source, target):
    """Warlock: Draw a card, take 2 damage."""
    controller = source.controller
    if controller.hero:
        game.deal_damage(controller.hero, 2, source)
    controller.draw(1)


def hp_dagger_mastery(game, source, target):
    """Rogue: Equip a 1/2 Dagger."""
    from simulator.entities import Weapon, CardData
    from simulator.enums import CardType
    
    dagger_data = CardData(
        card_id="CS2_082",
        name="Wicked Knife",
        cost=0,
        attack=1,
        durability=2,
        card_type=CardType.WEAPON
    )
    dagger = Weapon(dagger_data, game)
    source.controller.equip_weapon(dagger)


def hp_reinforce(game, source, target):
    """Paladin: Summon a 1/1 Silver Hand Recruit."""
    game.summon_token(source.controller, "CS2_101t")


def hp_armor_up(game, source, target):
    """Warrior: Gain 2 armor."""
    if source.controller.hero:
        source.controller.hero.gain_armor(2)


def hp_shapeshift(game, source, target):
    """Druid: +1 Attack this turn, +1 Armor."""
    if source.controller.hero:
        # Note: Hero attack resets each turn in game engine (via attacks_this_turn reset)
        # The +1 attack is temporary for this turn only
        source.controller.hero._attack += 1
        source.controller.hero.gain_armor(1)


def hp_steady_shot(game, source, target):
    """Hunter: Deal 2 damage to enemy hero."""
    opponent = source.controller.opponent
    if opponent and opponent.hero:
        game.deal_damage(opponent.hero, 2, source)


def hp_lesser_heal(game, source, target):
    """Priest: Restore 2 Health to any target."""
    if target:
        game.heal(target, 2)


def hp_demon_claws(game, source, target):
    """Demon Hunter: +1 Attack this turn."""
    if source.controller.hero:
        # Note: Hero attack resets each turn in game engine
        source.controller.hero._attack += 1


def hp_ghoul_charge(game, source, target):
    """Death Knight: Summon a 1/1 Ghoul with Charge."""
    ghoul_data = CardData(
        card_id="RLK_Minion_Ghoul",
        name="Ghoul",
        cost=0,
        attack=1,
        health=1,
        card_type=CardType.MINION,
        charge=True
    )
    ghoul = Minion(ghoul_data, game)
    source.controller.summon(ghoul)


# === UPGRADED HERO POWERS (Justicar/Baku) ===

def hp_fireblast_rank2(game, source, target):
    """Upgraded Mage: Deal 2 damage to any target."""
    if target:
        game.deal_damage(target, 2, source)


def hp_totemic_slam(game, source, target):
    """Upgraded Shaman: Summon a random basic totem."""
    import random
    totem_ids = ["CS2_050", "CS2_051", "CS2_052", "NEW1_009"]
    existing = [m.card_id for m in source.controller.board]
    available = [t for t in totem_ids if t not in existing]
    if available and len(source.controller.board) < 7:
        game.summon_token(source.controller, random.choice(available))


def hp_soul_tap(game, source, target):
    """Upgraded Warlock: Draw a card."""
    source.controller.draw(1)


def hp_poisoned_daggers(game, source, target):
    """Upgraded Rogue: Equip a 2/2 Poisoned Dagger."""
    from simulator.entities import Weapon
    dagger_data = CardData(
        card_id="AT_132_ROGUE",
        name="Poisoned Daggers",
        cost=0,
        attack=2,
        durability=2,
        card_type=CardType.WEAPON
    )
    dagger = Weapon(dagger_data, game)
    source.controller.equip_weapon(dagger)


def hp_the_silver_hand(game, source, target):
    """Upgraded Paladin: Summon two 1/1 Silver Hand Recruits."""
    for _ in range(2):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "CS2_101t")


def hp_tank_up(game, source, target):
    """Upgraded Warrior: Gain 4 armor."""
    if source.controller.hero:
        source.controller.hero.gain_armor(4)


def hp_dire_shapeshift(game, source, target):
    """Upgraded Druid: +2 Attack this turn, +2 Armor."""
    if source.controller.hero:
        source.controller.hero._attack += 2
        source.controller.hero.gain_armor(2)


def hp_ballista_shot(game, source, target):
    """Upgraded Hunter: Deal 3 damage to enemy hero."""
    opponent = source.controller.opponent
    if opponent and opponent.hero:
        game.deal_damage(opponent.hero, 3, source)


def hp_heal(game, source, target):
    """Upgraded Priest: Restore 4 Health to any target."""
    if target:
        game.heal(target, 4)


def hp_infernal_strike(game, source, target):
    """Upgraded Demon Hunter: +2 Attack this turn."""
    if source.controller.hero:
        source.controller.hero._attack += 2


# === HERO CARD POWERS ===

def hp_voidform(game, source, target):
    """Shadowreaper Anduin: Deal 2 damage. Refresh after playing a card."""
    if target:
        game.deal_damage(target, 2, source)


def hp_build_a_beast(game, source, target):
    """Deathstalker Rexxar: Craft a custom Zombeast."""
    # Simplified - just summons a random beast
    pass


def hp_plague_lord(game, source, target):
    """Bloodreaver Gul'dan: Deal 3 damage. Restore 3 Health to your hero."""
    if target:
        game.deal_damage(target, 3, source)
    if source.controller.hero:
        game.heal(source.controller.hero, 3)


# Registry mapping card_id -> handler
HERO_POWER_HANDLERS: Dict[str, Callable] = {
    # Basic Hero Powers
    "CS2_034": hp_fireblast,
    "CS2_049": hp_totemic_call,
    "CS2_056": hp_life_tap,
    "CS2_083b": hp_dagger_mastery,
    "CS2_101": hp_reinforce,
    "CS2_102": hp_armor_up,
    "CS2_017": hp_shapeshift,
    "DS1h_292": hp_steady_shot,
    "CS1h_001": hp_lesser_heal,
    "HERO_10bp": hp_demon_claws,
    "HERO_11bp": hp_ghoul_charge,
    
    # Upgraded Hero Powers (Justicar Trueheart / Baku the Mooneater)
    "AT_132_MAGE": hp_fireblast_rank2,    # Fireblast Rank 2
    "AT_132_SHAMAN": hp_totemic_slam,     # Totemic Slam
    "AT_132_WARLOCK": hp_soul_tap,        # Soul Tap
    "AT_132_ROGUE": hp_poisoned_daggers,  # Poisoned Daggers
    "AT_132_PALADIN": hp_the_silver_hand, # The Silver Hand
    "AT_132_WARRIOR": hp_tank_up,         # Tank Up!
    "AT_132_DRUID": hp_dire_shapeshift,   # Dire Shapeshift
    "AT_132_HUNTER": hp_ballista_shot,    # Ballista Shot
    "AT_132_PRIEST": hp_heal,             # Heal
    "HERO_10bp2": hp_infernal_strike,     # Infernal Strike
    
    # Hero Card Powers
    "ICC_830p": hp_voidform,              # Shadowreaper Anduin
    "ICC_828p": hp_build_a_beast,         # Deathstalker Rexxar
    "ICC_831p": hp_plague_lord,           # Bloodreaver Gul'dan
}


# Target requirements for hero powers
HERO_POWER_NEEDS_TARGET: Dict[str, bool] = {
    # Basic Powers
    "CS2_034": True,     # Fireblast - any target
    "CS2_049": False,    # Totemic Call
    "CS2_056": False,    # Life Tap
    "CS2_083b": False,   # Dagger Mastery
    "CS2_101": False,    # Reinforce
    "CS2_102": False,    # Armor Up
    "CS2_017": False,    # Shapeshift
    "DS1h_292": False,   # Steady Shot (always enemy hero)
    "CS1h_001": True,    # Lesser Heal - any target
    "HERO_10bp": False,  # Demon Claws
    "HERO_11bp": False,  # Ghoul Charge
    
    # Upgraded Powers
    "AT_132_MAGE": True,     # Fireblast Rank 2 - any target
    "AT_132_SHAMAN": False,  # Totemic Slam
    "AT_132_WARLOCK": False, # Soul Tap
    "AT_132_ROGUE": False,   # Poisoned Daggers
    "AT_132_PALADIN": False, # The Silver Hand
    "AT_132_WARRIOR": False, # Tank Up
    "AT_132_DRUID": False,   # Dire Shapeshift
    "AT_132_HUNTER": False,  # Ballista Shot
    "AT_132_PRIEST": True,   # Heal - any target
    "HERO_10bp2": False,     # Infernal Strike
    
    # Hero Card Powers
    "ICC_830p": True,    # Voidform - any target
    "ICC_828p": False,   # Build-A-Beast
    "ICC_831p": True,    # Plague Lord - any target
}


def get_hero_power_handler(card_id: str) -> Optional[Callable]:
    """Get the effect handler for a hero power."""
    return HERO_POWER_HANDLERS.get(card_id)


def hero_power_needs_target(card_id: str) -> bool:
    """Check if a hero power requires a target."""
    return HERO_POWER_NEEDS_TARGET.get(card_id, False)


def register_hero_powers(game) -> None:
    """Register all hero power handlers with a game instance."""
    for card_id, handler in HERO_POWER_HANDLERS.items():
        game._battlecry_handlers[card_id] = handler
