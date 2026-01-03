"""GVG Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS ===

# GVG_069 - Antique Healbot
def effect_GVG_069_battlecry(game, source, target):
    """Antique Healbot: Battlecry: Restore 8 Health to your hero."""
    if source.controller.hero:
        game.heal(source.controller.hero, 8)


# GVG_076 - Explosive Sheep
def effect_GVG_076_deathrattle(game, source, target):
    """Explosive Sheep: Deathrattle: Deal 2 damage to all minions."""
    for p in game.players:
        for m in p.board[:]:
            game.deal_damage(m, 2)


# GVG_090 - Madder Bomber
def effect_GVG_090_battlecry(game, source, target):
    """Madder Bomber: Battlecry: Deal 6 damage randomly split among all other characters."""
    for _ in range(6):
        all_chars = []
        for p in game.players:
            if p.hero:
                all_chars.append(p.hero)
            all_chars.extend(p.board)
        all_chars = [c for c in all_chars if c != source and getattr(c, 'health', 1) > 0]
        if all_chars:
            game.deal_damage(random.choice(all_chars), 1)


# GVG_096 - Piloted Shredder
def effect_GVG_096_deathrattle(game, source, target):
    """Piloted Shredder: Deathrattle: Summon a random 2-Cost minion."""
    from simulator.card_loader import CardDatabase
    from simulator.enums import CardType
    
    db = CardDatabase.get_instance()
    db.load()
    
    two_cost_minions = [
        cid for cid, card in db._cards.items() 
        if card.card_type == CardType.MINION and card.cost == 2 and card.collectible
    ]
    
    if two_cost_minions and len(source.controller.board) < 7:
        chosen = random.choice(two_cost_minions)
        game.summon_token(source.controller, chosen)


# GVG_082 - Clockwork Gnome
def effect_GVG_082_deathrattle(game, source, target):
    """Clockwork Gnome: Deathrattle: Add a Spare Part card to your hand."""
    spare_parts = [
        "PART_001",  # Armor Plating
        "PART_002",  # Time Rewinder
        "PART_003",  # Rusty Horn
        "PART_004",  # Finicky Cloakfield
        "PART_005",  # Emergency Coolant
        "PART_006",  # Reversing Switch
        "PART_007",  # Whirling Blades
    ]
    from simulator.card_loader import create_card
    part = create_card(random.choice(spare_parts), game)
    source.controller.add_to_hand(part)


# GVG_078 - Mechanical Yeti
def effect_GVG_078_deathrattle(game, source, target):
    """Mechanical Yeti: Deathrattle: Give each player a Spare Part."""
    spare_parts = [
        "PART_001", "PART_002", "PART_003", "PART_004",
        "PART_005", "PART_006", "PART_007",
    ]
    from simulator.card_loader import create_card
    for p in game.players:
        part = create_card(random.choice(spare_parts), game)
        p.add_to_hand(part)


# === SPELLS / SPARE PARTS ===

# PART_001 - Armor Plating
def effect_PART_001_battlecry(game, source, target):
    """Armor Plating: Give a minion +1 Health."""
    if target:
        target._health += 1
        target.max_health += 1


# PART_002 - Time Rewinder
def effect_PART_002_battlecry(game, source, target):
    """Time Rewinder: Return a friendly minion to your hand."""
    if target and target.controller == source.controller:
        game.return_to_hand(target)


# PART_003 - Rusty Horn
def effect_PART_003_battlecry(game, source, target):
    """Rusty Horn: Give a minion Taunt."""
    if target:
        target.taunt = True


# PART_004 - Finicky Cloakfield
def effect_PART_004_battlecry(game, source, target):
    """Finicky Cloakfield: Give a friendly minion Stealth until your next turn."""
    if target:
        target.stealth = True


# PART_005 - Emergency Coolant
def effect_PART_005_battlecry(game, source, target):
    """Emergency Coolant: Freeze a minion."""
    if target and hasattr(target, 'frozen'):
        target.frozen = True


# PART_006 - Reversing Switch
def effect_PART_006_battlecry(game, source, target):
    """Reversing Switch: Swap a minion's Attack and Health."""
    if target:
        old_attack = target.attack
        old_health = target.health
        target._attack = old_health
        target._health = old_attack
        target.max_health = old_attack


# PART_007 - Whirling Blades
def effect_PART_007_battlecry(game, source, target):
    """Whirling Blades: Give a minion +1 Attack."""
    if target:
        target._attack += 1


# Registry
GVG_EFFECTS = {
    # Battlecries
    "GVG_069": effect_GVG_069_battlecry,
    "GVG_090": effect_GVG_090_battlecry,
    # Deathrattles
    "GVG_076": effect_GVG_076_deathrattle,
    "GVG_082": effect_GVG_082_deathrattle,
    "GVG_078": effect_GVG_078_deathrattle,
    "GVG_096": effect_GVG_096_deathrattle,
    # Spare Parts
    "PART_001": effect_PART_001_battlecry,
    "PART_002": effect_PART_002_battlecry,
    "PART_003": effect_PART_003_battlecry,
    "PART_004": effect_PART_004_battlecry,
    "PART_005": effect_PART_005_battlecry,
    "PART_006": effect_PART_006_battlecry,
    "PART_007": effect_PART_007_battlecry,
}
