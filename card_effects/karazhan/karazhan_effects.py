"""One Night in Karazhan Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS ===

# KAR_005 - Kindly Grandmother
def effect_KAR_005_deathrattle(game, source, target):
    """Kindly Grandmother: Deathrattle: Summon a 3/2 Big Bad Wolf."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "KAR_005a")


# KAR_009 - Babbling Book
def effect_KAR_009_battlecry(game, source, target):
    """Babbling Book: Battlecry: Add a random Mage spell to your hand."""
    from simulator.card_loader import CardDatabase
    from simulator.enums import CardType, CardClass
    
    db = CardDatabase.get_instance()
    db.load()
    
    mage_spells = [
        cid for cid, card in db._cards.items()
        if card.card_type == CardType.SPELL and card.card_class == CardClass.MAGE and card.collectible
    ]
    if mage_spells:
        from simulator.card_loader import create_card
        spell = create_card(random.choice(mage_spells), game)
        source.controller.add_to_hand(spell)


# KAR_029 - Runic Egg
def effect_KAR_029_deathrattle(game, source, target):
    """Runic Egg: Deathrattle: Draw a card."""
    source.controller.draw(1)


# KAR_035 - Priest of the Feast
def effect_KAR_035_trigger(game, source, spell_event):
    """Priest of the Feast: Whenever you cast a spell, restore 3 Health to your hero."""
    if source.controller.hero:
        game.heal(source.controller.hero, 3)


# KAR_036 - Arcane Anomaly
def effect_KAR_036_trigger(game, source, spell_event):
    """Arcane Anomaly: Whenever you cast a spell, gain +1 Health."""
    source._health += 1
    source.max_health += 1


# KAR_041 - Moat Lurker
def effect_KAR_041_battlecry(game, source, target):
    """Moat Lurker: Battlecry: Destroy a minion."""
    if target and target.card_type.name == 'MINION':
        # Store the destroyed minion for deathrattle
        source._destroyed_target = target.card_id
        game.destroy(target)


def effect_KAR_041_deathrattle(game, source, target):
    """Moat Lurker: Deathrattle: Resummon the destroyed minion."""
    destroyed_id = getattr(source, '_destroyed_target', None)
    if destroyed_id and len(source.controller.board) < 7:
        game.summon_token(source.controller, destroyed_id)


# KAR_044 - Moroes
def effect_KAR_044_trigger(game, source, turn_end):
    """Moroes: At the end of your turn, summon a 1/1 Steward."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "KAR_044a")


# KAR_061 - The Curator
def effect_KAR_061_battlecry(game, source, target):
    """The Curator: Battlecry: Draw a Beast, Dragon, and Murloc from your deck."""
    from simulator.enums import Race
    
    deck = source.controller.deck
    for race in [Race.BEAST, Race.DRAGON, Race.MURLOC]:
        for card in deck[:]:
            if hasattr(card.data, 'race') and card.data.race == race:
                deck.remove(card)
                source.controller.add_to_hand(card)
                break


# KAR_089 - Malchezaar's Imp
def effect_KAR_089_trigger(game, source, discard_event):
    """Malchezaar's Imp: Whenever you discard a card, draw a card."""
    source.controller.draw(1)


# KAR_092 - Medivh's Valet
def effect_KAR_092_battlecry(game, source, target):
    """Medivh's Valet: Battlecry: If you control a Secret, deal 3 damage."""
    if getattr(source.controller, 'secrets', []) and target:
        game.deal_damage(target, 3)


# KAR_094 - Deadly Fork
def effect_KAR_094_deathrattle(game, source, target):
    """Deadly Fork: Deathrattle: Add a 3/2 Sharp Fork to your hand."""
    from simulator.card_loader import create_card
    fork = create_card("KAR_094a", game)
    source.controller.add_to_hand(fork)


# KAR_097 - Medivh, the Guardian
def effect_KAR_097_battlecry(game, source, target):
    """Medivh: Battlecry: Equip Atiesh, a 1/3 weapon."""
    from simulator.card_loader import create_card
    weapon = create_card("KAR_097t", game)
    if weapon:
        source.controller.equip_weapon(weapon)


# KAR_114 - Barnes
def effect_KAR_114_battlecry(game, source, target):
    """Barnes: Battlecry: Summon a 1/1 copy of a random minion in your deck."""
    from simulator.enums import CardType
    
    minions = [c for c in source.controller.deck if c.card_type == CardType.MINION]
    if minions and len(source.controller.board) < 7:
        chosen = random.choice(minions)
        game.summon_token(source.controller, chosen.card_id)
        # Set stats to 1/1 on the summoned copy
        summoned = source.controller.board[-1]
        summoned._attack = 1
        summoned._health = 1
        summoned.max_health = 1


# KAR_204 - Onyx Bishop
def effect_KAR_204_battlecry(game, source, target):
    """Onyx Bishop: Battlecry: Summon a friendly minion that died this game."""
    dead = getattr(source.controller, 'dead_minions', [])
    if dead and len(source.controller.board) < 7:
        game.summon_token(source.controller, random.choice(dead))


# KAR_710 - Arcanosmith
def effect_KAR_710_battlecry(game, source, target):
    """Arcanosmith: Battlecry: Summon a 0/5 minion with Taunt."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "KAR_710m")


# === SPELLS ===

# KAR_013 - Purify
def effect_KAR_013_battlecry(game, source, target):
    """Purify: Silence a friendly minion. Draw a card."""
    if target and target.controller == source.controller:
        game.silence(target)
    source.controller.draw(1)


# KAR_073 - Maelstrom Portal
def effect_KAR_073_battlecry(game, source, target):
    """Maelstrom Portal: Deal 1 damage to all enemy minions. Summon a random 1-Cost minion."""
    for minion in source.controller.opponent.board[:]:
        game.deal_damage(minion, 1)
    
    from simulator.card_loader import CardDatabase
    from simulator.enums import CardType
    
    db = CardDatabase.get_instance()
    db.load()
    
    one_cost = [
        cid for cid, card in db._cards.items()
        if card.card_type == CardType.MINION and card.cost == 1 and card.collectible
    ]
    if one_cost and len(source.controller.board) < 7:
        game.summon_token(source.controller, random.choice(one_cost))


# KAR_075 - Moonglade Portal
def effect_KAR_075_battlecry(game, source, target):
    """Moonglade Portal: Restore 6 Health. Summon a random 6-Cost minion."""
    if target:
        game.heal(target, 6)
    
    from simulator.card_loader import CardDatabase
    from simulator.enums import CardType
    
    db = CardDatabase.get_instance()
    db.load()
    
    six_cost = [
        cid for cid, card in db._cards.items()
        if card.card_type == CardType.MINION and card.cost == 6 and card.collectible
    ]
    if six_cost and len(source.controller.board) < 7:
        game.summon_token(source.controller, random.choice(six_cost))


# KAR_076 - Firelands Portal
def effect_KAR_076_battlecry(game, source, target):
    """Firelands Portal: Deal 5 damage. Summon a random 5-Cost minion."""
    if target:
        game.deal_damage(target, 5)
    
    from simulator.card_loader import CardDatabase
    from simulator.enums import CardType
    
    db = CardDatabase.get_instance()
    db.load()
    
    five_cost = [
        cid for cid, card in db._cards.items()
        if card.card_type == CardType.MINION and card.cost == 5 and card.collectible
    ]
    if five_cost and len(source.controller.board) < 7:
        game.summon_token(source.controller, random.choice(five_cost))


# KAR_091 - Ironforge Portal
def effect_KAR_091_battlecry(game, source, target):
    """Ironforge Portal: Gain 4 Armor. Summon a random 4-Cost minion."""
    if source.controller.hero:
        source.controller.hero._armor = getattr(source.controller.hero, '_armor', 0) + 4
    
    from simulator.card_loader import CardDatabase
    from simulator.enums import CardType
    
    db = CardDatabase.get_instance()
    db.load()
    
    four_cost = [
        cid for cid, card in db._cards.items()
        if card.card_type == CardType.MINION and card.cost == 4 and card.collectible
    ]
    if four_cost and len(source.controller.board) < 7:
        game.summon_token(source.controller, random.choice(four_cost))


# Registry
KARAZHAN_EFFECTS = {
    # Battlecries
    "KAR_009": effect_KAR_009_battlecry,
    "KAR_041": effect_KAR_041_battlecry,
    "KAR_061": effect_KAR_061_battlecry,
    "KAR_092": effect_KAR_092_battlecry,
    "KAR_097": effect_KAR_097_battlecry,
    "KAR_114": effect_KAR_114_battlecry,
    "KAR_204": effect_KAR_204_battlecry,
    "KAR_710": effect_KAR_710_battlecry,
    # Deathrattles
    "KAR_005": effect_KAR_005_deathrattle,
    "KAR_029": effect_KAR_029_deathrattle,
    "KAR_094": effect_KAR_094_deathrattle,
    # Triggers
    "KAR_035": effect_KAR_035_trigger,
    "KAR_036": effect_KAR_036_trigger,
    "KAR_044": effect_KAR_044_trigger,
    "KAR_089": effect_KAR_089_trigger,
    # Spells
    "KAR_013": effect_KAR_013_battlecry,
    "KAR_073": effect_KAR_073_battlecry,
    "KAR_075": effect_KAR_075_battlecry,
    "KAR_076": effect_KAR_076_battlecry,
    "KAR_091": effect_KAR_091_battlecry,
}
