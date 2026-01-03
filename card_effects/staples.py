"""Evergreen Staple Card Effects.

This module contains effects for commonly used cards across formats:
- Neutral staples
- Weapon effects
- Rush/Charge minions
- Discover cards (simplified)
"""

import random
from typing import List, Optional


# === DISCOVER HELPERS ===

def _discover_from_pool(game, player, card_pool: List[str], count: int = 3) -> Optional[str]:
    """Simplified Discover: Pick a random card from pool and add to hand.
    
    Note: Full Discover would show 3 options and let player choose.
    This simplified version just picks randomly.
    """
    if not card_pool:
        return None
    
    from simulator.card_loader import create_card
    chosen_id = random.choice(card_pool[:count] if len(card_pool) >= count else card_pool)
    card = create_card(chosen_id, game)
    if card:
        player.add_to_hand(card)
    return chosen_id


def _get_class_cards(game, card_class, card_type=None) -> List[str]:
    """Get collectible cards of a specific class."""
    from simulator.card_loader import CardDatabase
    from simulator.enums import CardType
    
    db = CardDatabase.get_instance()
    db.load()
    
    cards = []
    for cid, card in db._cards.items():
        if card.card_class == card_class and card.collectible:
            if card_type is None or card.card_type == card_type:
                cards.append(cid)
    return cards


# === NEUTRAL STAPLES ===

# BOT_548 - Zilliax (Boomsday)
def effect_BOT_548_battlecry(game, source, target):
    """Zilliax: Magnetic, Divine Shield, Taunt, Lifesteal, Rush.
    
    Note: Keywords are already set on the card data.
    This handles Magnetic (fuse with a Mech).
    """
    from simulator.enums import Race
    if target and hasattr(target.data, 'race') and target.data.race == Race.MECHANICAL:
        # Magnetic: Fuse with target mech
        target._attack += source.attack
        target._health += source.health
        target.max_health += source.max_health
        target._divine_shield = True
        target._taunt = True
        target._lifesteal = True
        target._rush = True
        # Remove Zilliax from board (it fused)
        if source in source.controller.board:
            source.controller.board.remove(source)


# EX1_012 - Bloodmage Thalnos
def effect_EX1_012_deathrattle(game, source, target):
    """Bloodmage Thalnos: Spell Damage +1. Deathrattle: Draw a card."""
    source.controller.draw(1)


# EX1_016 - Sylvanas Windrunner
def effect_EX1_016_deathrattle(game, source, target):
    """Sylvanas Windrunner: Deathrattle: Take control of a random enemy minion."""
    enemy_minions = list(source.controller.opponent.board)
    if enemy_minions and len(source.controller.board) < 7:
        stolen = random.choice(enemy_minions)
        source.controller.opponent.board.remove(stolen)
        stolen.controller = source.controller
        source.controller.board.append(stolen)


# EX1_561 - Alexstrasza
def effect_EX1_561_battlecry(game, source, target):
    """Alexstrasza: Battlecry: Set a hero's remaining Health to 15."""
    if target and target.card_type.name == 'HERO':
        # Set health to 15
        current = target.health
        if current > 15:
            target._damage = target.max_health - 15
        else:
            # Heal up to 15
            target._damage = max(0, target.max_health - 15)


# EX1_572 - Ysera
def effect_EX1_572_trigger(game, source, turn_end):
    """Ysera: At the end of your turn, add a Dream Card to your hand."""
    dream_cards = ["DREAM_01", "DREAM_02", "DREAM_03", "DREAM_04", "DREAM_05"]
    from simulator.card_loader import create_card
    card = create_card(random.choice(dream_cards), game)
    if card:
        source.controller.add_to_hand(card)


# EX1_062 - Old Murk-Eye
def effect_EX1_062_aura(game, source):
    """Old Murk-Eye: Charge. Has +1 Attack for each other Murloc on the battlefield."""
    from simulator.enums import Race
    murloc_count = 0
    for p in game.players:
        for m in p.board:
            if m != source and hasattr(m.data, 'race') and m.data.race == Race.MURLOC:
                murloc_count += 1
    source._attack = source.data.attack + murloc_count


# === WEAPON EFFECTS ===

# CS2_106 - Fiery War Axe
# (No effect - just stats)

# EX1_133 - Perdition's Blade
def effect_EX1_133_battlecry(game, source, target):
    """Perdition's Blade: Battlecry: Deal 1 damage. Combo: Deal 2 instead."""
    damage = 1
    if getattr(source.controller, 'cards_played_this_turn', 0) > 0:
        damage = 2
    if target:
        game.deal_damage(target, damage)


# CS2_080 - Assassin's Blade
# (No effect - just stats)

# EX1_247 - Argent Commander
def effect_EX1_247_battlecry(game, source, target):
    """Argent Commander: Charge, Divine Shield.
    
    Note: Keywords set on card data, no battlecry needed.
    """
    pass


# === WEAPON BUFF SPELLS ===

# CS2_074 - Deadly Poison
def effect_CS2_074_battlecry(game, source, target):
    """Deadly Poison: Give your weapon +2 Attack."""
    if source.controller.weapon:
        source.controller.weapon._attack += 2


# EX1_409 - Upgrade!
def effect_EX1_409_battlecry(game, source, target):
    """Upgrade!: If you have a weapon, give it +1/+1. Otherwise, equip a 1/3 weapon."""
    if source.controller.weapon:
        source.controller.weapon._attack += 1
        source.controller.weapon._durability += 1
    else:
        from simulator.entities import Weapon, CardData
        from simulator.enums import CardType
        axe_data = CardData(
            card_id="EX1_409t",
            name="Heavy Axe",
            cost=0,
            attack=1,
            durability=3,
            card_type=CardType.WEAPON
        )
        axe = Weapon(axe_data, game)
        source.controller.equip_weapon(axe)


# === DISCOVER CARDS ===

# LOE_023 - Dark Peddler
def effect_LOE_023_battlecry(game, source, target):
    """Dark Peddler: Battlecry: Discover a 1-Cost card."""
    from simulator.card_loader import CardDatabase
    
    db = CardDatabase.get_instance()
    db.load()
    
    one_cost = [cid for cid, card in db._cards.items() if card.cost == 1 and card.collectible]
    if one_cost:
        _discover_from_pool(game, source.controller, one_cost)


# UNG_937 - Primalfin Lookout (already in ungoro)

# CS2_029 - Fireball (already in classic)


# === CARD DRAW ===

# EX1_284 - Azure Drake
def effect_EX1_284_battlecry(game, source, target):
    """Azure Drake: Spell Damage +1. Battlecry: Draw a card."""
    source.controller.draw(1)


# CS2_022 - Polymorph
def effect_CS2_022_battlecry(game, source, target):
    """Polymorph: Transform a minion into a 1/1 Sheep."""
    if target and target.card_type.name == 'MINION':
        game.transform(target, "CS2_tk1")


# EX1_246 - Hex
def effect_EX1_246_battlecry(game, source, target):
    """Hex: Transform a minion into a 0/1 Frog with Taunt."""
    if target and target.card_type.name == 'MINION':
        game.transform(target, "hexfrog")


# CS2_023 - Arcane Intellect
def effect_CS2_023_battlecry(game, source, target):
    """Arcane Intellect: Draw 2 cards."""
    source.controller.draw(2)


# EX1_145 - Preparation
def effect_EX1_145_battlecry(game, source, target):
    """Preparation: The next spell you cast this turn costs (2) less."""
    source.controller.next_spell_cost_reduction = 2


# CS2_011 - Savage Roar
def effect_CS2_011_battlecry(game, source, target):
    """Savage Roar: Give your characters +2 Attack this turn."""
    if source.controller.hero:
        source.controller.hero._attack += 2
    for minion in source.controller.board:
        minion._attack += 2


# Registry
STAPLE_EFFECTS = {
    # Neutral minions
    "BOT_548": effect_BOT_548_battlecry,  # Zilliax
    "EX1_012": effect_EX1_012_deathrattle,  # Bloodmage Thalnos
    "EX1_016": effect_EX1_016_deathrattle,  # Sylvanas
    "EX1_561": effect_EX1_561_battlecry,    # Alexstrasza
    "EX1_572": effect_EX1_572_trigger,      # Ysera
    # Weapons
    "EX1_133": effect_EX1_133_battlecry,  # Perdition's Blade
    # Weapon buffs
    "CS2_074": effect_CS2_074_battlecry,  # Deadly Poison
    "EX1_409": effect_EX1_409_battlecry,  # Upgrade!
    # Discover
    "LOE_023": effect_LOE_023_battlecry,  # Dark Peddler
    # Card draw / spells
    "EX1_284": effect_EX1_284_battlecry,  # Azure Drake
    "CS2_022": effect_CS2_022_battlecry,  # Polymorph
    "EX1_246": effect_EX1_246_battlecry,  # Hex
    "CS2_023": effect_CS2_023_battlecry,  # Arcane Intellect
    "EX1_145": effect_EX1_145_battlecry,  # Preparation
    "CS2_011": effect_CS2_011_battlecry,  # Savage Roar
}
