"""Blackrock Mountain Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS ===

# BRM_002 - Flamewaker
def effect_BRM_002_trigger(game, source, spell_event):
    """Flamewaker: After you cast a spell, deal 2 damage randomly split among all enemies."""
    targets = list(source.controller.opponent.board) + [source.controller.opponent.hero]
    targets = [t for t in targets if t and getattr(t, 'health', 1) > 0]
    for _ in range(2):
        if targets:
            game.deal_damage(random.choice(targets), 1)


# BRM_006 - Imp Gang Boss
def effect_BRM_006_trigger(game, source, damage_event):
    """Imp Gang Boss: Whenever this minion takes damage, summon a 1/1 Imp."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "BRM_006t")


# BRM_008 - Dark Iron Skulker
def effect_BRM_008_battlecry(game, source, target):
    """Dark Iron Skulker: Battlecry: Deal 2 damage to all undamaged enemy minions."""
    for m in source.controller.opponent.board[:]:
        if m.damage == 0:
            game.deal_damage(m, 2)


# BRM_016 - Axe Flinger
def effect_BRM_016_trigger(game, source, damage_event):
    """Axe Flinger: Whenever this minion takes damage, deal 2 damage to the enemy hero."""
    if source.controller.opponent.hero:
        game.deal_damage(source.controller.opponent.hero, 2)


# BRM_019 - Grim Patron  
def effect_BRM_019_trigger(game, source, damage_event):
    """Grim Patron: Whenever this minion survives damage, summon another Grim Patron."""
    if source.health > 0 and len(source.controller.board) < 7:
        game.summon_token(source.controller, "BRM_019")


# BRM_022 - Dragon Egg
def effect_BRM_022_trigger(game, source, damage_event):
    """Dragon Egg: Whenever this minion takes damage, summon a 2/1 Whelp."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "BRM_022t")


# BRM_026 - Hungry Dragon
def effect_BRM_026_battlecry(game, source, target):
    """Hungry Dragon: Battlecry: Summon a random 1-Cost minion for your opponent."""
    from simulator.card_loader import CardDatabase
    from simulator.enums import CardType
    
    db = CardDatabase.get_instance()
    db.load()
    
    one_cost = [
        cid for cid, card in db._cards.items()
        if card.card_type == CardType.MINION and card.cost == 1 and card.collectible
    ]
    if one_cost and len(source.controller.opponent.board) < 7:
        game.summon_token(source.controller.opponent, random.choice(one_cost))


# BRM_027 - Majordomo Executus
def effect_BRM_027_deathrattle(game, source):
    """Majordomo Executus: Deathrattle: Replace your hero with Ragnaros the Firelord."""
    # Complex hero replacement - simplified to just summon Ragnaros token
    pass  # Requires hero replacement logic


# BRM_028 - Emperor Thaurissan
def effect_BRM_028_trigger(game, source, turn_end):
    """Emperor Thaurissan: At the end of your turn, reduce the Cost of cards in your hand by (1)."""
    for card in source.controller.hand:
        if hasattr(card, 'cost') and card.cost > 0:
            card.cost -= 1


# BRM_029 - Rend Blackhand
def effect_BRM_029_battlecry(game, source, target):
    """Rend Blackhand: Battlecry: If you're holding a Dragon, destroy a Legendary minion."""
    from simulator.enums import Rarity, Race
    holding_dragon = any(getattr(c.data, 'race', None) == Race.DRAGON for c in source.controller.hand)
    if target and holding_dragon and getattr(target.data, 'rarity', None) == Rarity.LEGENDARY:
        game.destroy(target)


# BRM_030 - Nefarian
def effect_BRM_030_battlecry(game, source, target):
    """Nefarian: Battlecry: Add 2 random spells to your hand (from your opponent's class)."""
    from simulator.card_loader import CardDatabase, create_card
    from simulator.enums import CardType
    
    opponent_class = None
    if source.controller.opponent.hero:
        opponent_class = getattr(source.controller.opponent.hero.data, 'card_class', None)
    
    if opponent_class:
        db = CardDatabase.get_instance()
        db.load()
        class_spells = [
            cid for cid, card in db._cards.items()
            if card.card_type == CardType.SPELL and card.card_class == opponent_class and card.collectible
        ]
        for _ in range(2):
            if class_spells:
                spell_id = random.choice(class_spells)
                spell = create_card(spell_id, game)
                source.controller.add_to_hand(spell)


# BRM_031 - Chromaggus
def effect_BRM_031_trigger(game, source, draw_event):
    """Chromaggus: Whenever you draw a card, put another copy into your hand."""
    from simulator.card_loader import create_card
    if draw_event and hasattr(draw_event, 'card'):
        copy = create_card(draw_event.card.card_id, game)
        source.controller.add_to_hand(copy)


# BRM_033 - Blackwing Technician
def effect_BRM_033_battlecry(game, source, target):
    """Blackwing Technician: Battlecry: If you're holding a Dragon, gain +1/+1."""
    from simulator.enums import Race
    holding_dragon = any(getattr(c.data, 'race', None) == Race.DRAGON for c in source.controller.hand)
    if holding_dragon:
        source._attack += 1
        source._health += 1
        source.max_health += 1


# BRM_034 - Blackwing Corruptor
def effect_BRM_034_battlecry(game, source, target):
    """Blackwing Corruptor: Battlecry: If you're holding a Dragon, deal 3 damage."""
    from simulator.enums import Race
    holding_dragon = any(getattr(c.data, 'race', None) == Race.DRAGON for c in source.controller.hand)
    if target and holding_dragon:
        game.deal_damage(target, 3)


# === SPELLS ===

# BRM_001 - Solemn Vigil
def effect_BRM_001_battlecry(game, source, target):
    """Solemn Vigil: Draw 2 cards. Costs (1) less for each minion that died this turn."""
    source.controller.draw(2)


# BRM_003 - Dragon's Breath
def effect_BRM_003_battlecry(game, source, target):
    """Dragon's Breath: Deal 4 damage. Costs (1) less for each minion that died this turn."""
    if target:
        game.deal_damage(target, 4)


# BRM_005 - Demonwrath
def effect_BRM_005_battlecry(game, source, target):
    """Demonwrath: Deal 2 damage to all non-Demon minions."""
    from simulator.enums import Race
    for p in game.players:
        for m in p.board[:]:
            if getattr(m.data, 'race', None) != Race.DEMON:
                game.deal_damage(m, 2)


# BRM_007 - Gang Up
def effect_BRM_007_battlecry(game, source, target):
    """Gang Up: Choose a minion. Shuffle 3 copies of it into your deck."""
    if target:
        from simulator.card_loader import create_card
        for _ in range(3):
            copy = create_card(target.card_id, game)
            source.controller.deck.append(copy)
        random.shuffle(source.controller.deck)


# BRM_011 - Lava Shock
def effect_BRM_011_battlecry(game, source, target):
    """Lava Shock: Deal 2 damage. Unlock your Overloaded Mana Crystals."""
    if target:
        game.deal_damage(target, 2)
    source.controller.overload = 0
    source.controller.overload_next = 0


# BRM_013 - Quick Shot
def effect_BRM_013_battlecry(game, source, target):
    """Quick Shot: Deal 3 damage. If your hand is empty, draw a card."""
    if target:
        game.deal_damage(target, 3)
    if len(source.controller.hand) == 0:
        source.controller.draw(1)


# BRM_015 - Revenge
def effect_BRM_015_battlecry(game, source, target):
    """Revenge: Deal 1 damage to all minions. If you have 12 or less Health, deal 3 damage instead."""
    damage = 3 if source.controller.hero.health <= 12 else 1
    for p in game.players:
        for m in p.board[:]:
            game.deal_damage(m, damage)


# BRM_017 - Resurrect
def effect_BRM_017_battlecry(game, source, target):
    """Resurrect: Summon a random friendly minion that died this game."""
    from simulator.card_loader import create_card
    dead_minions = getattr(source.controller, 'graveyard', [])
    if dead_minions and len(source.controller.board) < 7:
        chosen = random.choice(dead_minions)
        game.summon_token(source.controller, chosen)


# Registry
BRM_EFFECTS = {
    # Triggers
    "BRM_002": effect_BRM_002_trigger,
    "BRM_006": effect_BRM_006_trigger,
    "BRM_016": effect_BRM_016_trigger,
    "BRM_019": effect_BRM_019_trigger,
    "BRM_022": effect_BRM_022_trigger,
    "BRM_028": effect_BRM_028_trigger,
    "BRM_031": effect_BRM_031_trigger,
    # Battlecries
    "BRM_008": effect_BRM_008_battlecry,
    "BRM_026": effect_BRM_026_battlecry,
    "BRM_029": effect_BRM_029_battlecry,
    "BRM_030": effect_BRM_030_battlecry,
    "BRM_033": effect_BRM_033_battlecry,
    "BRM_034": effect_BRM_034_battlecry,
    # Deathrattles
    "BRM_027": effect_BRM_027_deathrattle,
    # Spells
    "BRM_001": effect_BRM_001_battlecry,
    "BRM_003": effect_BRM_003_battlecry,
    "BRM_005": effect_BRM_005_battlecry,
    "BRM_007": effect_BRM_007_battlecry,
    "BRM_011": effect_BRM_011_battlecry,
    "BRM_013": effect_BRM_013_battlecry,
    "BRM_015": effect_BRM_015_battlecry,
    "BRM_017": effect_BRM_017_battlecry,
}
