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
    # Create ghoul token
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


# Registry mapping card_id -> handler
HERO_POWER_HANDLERS: Dict[str, Callable] = {
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
}


# Target requirements for hero powers
HERO_POWER_NEEDS_TARGET: Dict[str, bool] = {
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
