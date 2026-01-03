"""Scholomance Academy Card Effects - Manually implemented for key cards.

Note: Fireplace has minimal Scholomance support (only Transfer Student).
These effects are manually implemented based on card text.
"""

import random


# === SOUL FRAGMENT SYSTEM ===
# Soul Fragments are 0-cost cards that heal for 2 when drawn

def _shuffle_soul_fragment(game, player, count=1):
    """Shuffle Soul Fragments into a player's deck."""
    from simulator.card_loader import create_card
    for _ in range(count):
        fragment = create_card("SCH_307t", game)  # Soul Fragment token
        if fragment:
            player.deck.append(fragment)
    random.shuffle(player.deck)


# SCH_307t - Soul Fragment
def effect_SCH_307t_drawn(game, source, target):
    """Soul Fragment: Casts When Drawn - Restore 2 Health to your hero. Draw a card."""
    # This triggers when drawn, not when played
    if source.controller.hero:
        game.heal(source.controller.hero, 2)
    source.controller.draw(1)


# === LEGENDARY MINIONS ===

# SCH_351 - Jandice Barov
def effect_SCH_351_battlecry(game, source, target):
    """Jandice Barov: Battlecry: Summon two random 5-Cost minions. Secretly pick one that dies when it takes damage."""
    from simulator.card_loader import CardDatabase, create_card
    from simulator.enums import CardType
    
    db = CardDatabase.get_instance()
    db.load()
    
    five_cost = [
        cid for cid, card in db._cards.items()
        if card.card_type == CardType.MINION and card.cost == 5 and card.collectible
    ]
    
    summoned = []
    for _ in range(2):
        if five_cost and len(source.controller.board) < 7:
            chosen_id = random.choice(five_cost)
            minion = game.summon_token(source.controller, chosen_id)
            if minion:
                summoned.append(minion)
    
    # Randomly mark one as the illusion (dies when damaged)
    if summoned:
        illusion = random.choice(summoned)
        illusion._is_illusion = True  # Custom flag for Jandice illusion
        
        # Register trigger to die on damage
        # We need to define the handler here or use a generic one
        def illusion_damage_handler(game, source, target_damaged, amount, damage_source):
            if source == target_damaged:
                # Illusion took damage, destroy it
                source.destroy()
        
        # Register trigger
        # We access the game's internal trigger list directly as we don't have a public API for dynamic triggers yet
        if "on_damage_taken" in game._triggers:
            game._triggers["on_damage_taken"].append((illusion, illusion_damage_handler))


# SCH_514 - Lorekeeper Polkelt
def effect_SCH_514_battlecry(game, source, target):
    """Lorekeeper Polkelt: Battlecry: Reorder your deck from highest Cost to lowest Cost."""
    deck = source.controller.deck
    deck.sort(key=lambda c: c.cost, reverse=True)


# SCH_283 - Manafeeder Panthara
def effect_SCH_283_battlecry(game, source, target):
    """Manafeeder Panthara: Battlecry: If you've used your Hero Power this turn, draw a card."""
    if getattr(source.controller, 'hero_power_uses_this_turn', 0) > 0:
        source.controller.draw(1)


# SCH_519 - Vulpera Toxinblade
def effect_SCH_519_aura(game, source):
    """Vulpera Toxinblade: Your weapon has +2 Attack."""
    # Aura effect - would need aura system
    pass


# === DUAL-CLASS CARDS ===

# SCH_600 - Demon Companion (Hunter/Demon Hunter)
def effect_SCH_600_battlecry(game, source, target):
    """Demon Companion: Summon a random Demon Companion."""
    companions = ["SCH_600t1", "SCH_600t2", "SCH_600t3"]  # 1/2 Taunt, 2/1 Poison, 1/2 +1 Atk aura
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, random.choice(companions))


# SCH_312 - Initiation (Paladin/Priest)
def effect_SCH_312_battlecry(game, source, target):
    """Initiation: Give a minion +2/+6 and Taunt."""
    if target and target.card_type.name == 'MINION':
        target._attack += 2
        target._health += 6
        target.max_health += 6
        target._taunt = True


# SCH_537 - Trick Totem (Mage/Shaman)
def effect_SCH_537_trigger(game, source, turn_end):
    """Trick Totem: At the end of your turn, cast a random spell that costs (3) or less."""
    from simulator.card_loader import CardDatabase, create_card
    from simulator.enums import CardType, CardClass
    
    # 1. Get all eligible spells
    db = CardDatabase.get_instance()
    db.load()
    
    eligible = [
        cid for cid, card in db._cards.items()
        if card.card_type == CardType.SPELL and card.cost <= 3 and card.collectible
    ]
    
    if not eligible:
        return

    # 2. Pick one
    spell_id = random.choice(eligible)
    spell = create_card(spell_id, game)
    if not spell:
        return
        
    spell.controller = source.controller
    
    # 3. Determine target
    # This is simplified. Real HS checks specific targeting requirements.
    # We'll just pick a random character if the spell implies targeting.
    target = None
    all_targets = source.controller.board + source.controller.opponent.board
    if source.controller.hero: all_targets.append(source.controller.hero)
    if source.controller.opponent.hero: all_targets.append(source.controller.opponent.hero)
    
    if all_targets:
        target = random.choice(all_targets)
        
    # 4. Cast it (Bypassing mana, hand check)
    # We call the effect handler directly if we can find it, or use _play_spell approach
    # Since we aren't calling play_card, we manually trigger "on_spell_played" if we want
    # full accuracy, but Trick Totem *casts* it, so it should trigger events.
    # However, existing _play_spell logic in game.py is entangled with player stats.
    
    # Let's try to use the game's internal mechanism if possible, or just the effect.
    # Safe way:
    try:
        if spell.card_id in game._battlecry_handlers: # Spells use battlecry handlers in this codebase?
             # No, spells usually have their own handlers, but registered where?
             # verify_integration.py shows they are in _battlecry_handlers usually for spells too?
             # Let's check game.py _play_spell
             pass
    except:
        pass
        
    # Re-checking Game._play_spell
    if hasattr(game, '_play_spell'):
        # We need to monkey-patch or temporarily allow free cast? 
        # No, just call the effect handler directly.
         if spell.card_id in game._battlecry_handlers:
             game._battlecry_handlers[spell.card_id](game, spell, target)
             # Fire event
             game.fire_event("on_spell_played", spell, target)
             game.fire_event("on_after_card_played", spell)


# SCH_350 - Wand Thief (Mage/Rogue)
def effect_SCH_350_battlecry(game, source, target):
    """Wand Thief: Combo: Discover a Mage spell."""
    from simulator.card_loader import CardDatabase, create_card
    from simulator.enums import CardType, CardClass
    
    # Check for combo (if another card was played this turn)
    if getattr(source.controller, 'cards_played_this_turn', 0) > 0:
        db = CardDatabase.get_instance()
        db.load()
        
        mage_spells = [
            cid for cid, card in db._cards.items()
            if card.card_type == CardType.SPELL and card.card_class == CardClass.MAGE and card.collectible
        ]
        if mage_spells:
            spell = create_card(random.choice(mage_spells), game)
            source.controller.add_to_hand(spell)


# SCH_714 - Robes of Protection
def effect_SCH_714_aura(game, source):
    """Robes of Protection: Your minions have 'Can't be targeted by spells or Hero Powers.'"""
    # Aura effect - all friendly minions get elusive
    pass


# === SPELLBURST CARDS ===
# Spellburst triggers once when you cast a spell

# SCH_507 - Instructor Fireheart (Shaman)
def effect_SCH_507_spellburst(game, source, spell_event):
    """Instructor Fireheart: Spellburst: Add a random Shaman spell to your hand. It costs (1) and has Spellburst: Add another."""
    from simulator.card_loader import CardDatabase, create_card
    from simulator.enums import CardType, CardClass
    
    db = CardDatabase.get_instance()
    db.load()
    
    shaman_spells = [
        cid for cid, card in db._cards.items()
        if card.card_type == CardType.SPELL and card.card_class == CardClass.SHAMAN and card.collectible
    ]
    if shaman_spells:
        spell = create_card(random.choice(shaman_spells), game)
        if spell:
            spell._cost = 1
            source.controller.add_to_hand(spell)


# SCH_230 - Onyx Magescribe
def effect_SCH_230_spellburst(game, source, spell_event):
    """Onyx Magescribe: Spellburst: Add 2 random spells from your class to your hand."""
    from simulator.card_loader import CardDatabase, create_card
    from simulator.enums import CardType
    
    db = CardDatabase.get_instance()
    db.load()
    
    class_spells = [
        cid for cid, card in db._cards.items()
        if card.card_type == CardType.SPELL 
        and card.card_class == source.controller.hero.data.card_class 
        and card.collectible
    ]
    for _ in range(2):
        if class_spells:
            spell = create_card(random.choice(class_spells), game)
            source.controller.add_to_hand(spell)


# SCH_313 - Pen Flinger
def effect_SCH_313_battlecry(game, source, target):
    """Pen Flinger: Battlecry: Deal 1 damage to a minion."""
    if target and target.card_type.name == 'MINION':
        game.deal_damage(target, 1)


def effect_SCH_313_spellburst(game, source, spell_event):
    """Pen Flinger: Spellburst: Return this to your hand."""
    if source in source.controller.board:
        source.controller.board.remove(source)
        source.controller.add_to_hand(source)


# SCH_311 - Animated Broomstick
def effect_SCH_311_battlecry(game, source, target):
    """Animated Broomstick: Battlecry: Give your other minions Rush."""
    for minion in source.controller.board:
        if minion != source:
            minion._rush = True


# SCH_621 - Raise Dead (Warlock/Priest)
def effect_SCH_621_battlecry(game, source, target):
    """Raise Dead: Deal 3 damage to your hero. Return 2 friendly minions that died this game to your hand."""
    if source.controller.hero:
        game.deal_damage(source.controller.hero, 3)
    
    dead = getattr(source.controller, 'dead_minions', [])
    from simulator.card_loader import create_card
    for card_id in dead[:2]:
        card = create_card(card_id, game)
        if card:
            source.controller.add_to_hand(card)


# Registry
SCHOLOMANCE_EFFECTS = {
    # Battlecries
    "SCH_351": effect_SCH_351_battlecry,  # Jandice Barov
    "SCH_514": effect_SCH_514_battlecry,  # Lorekeeper Polkelt
    "SCH_283": effect_SCH_283_battlecry,  # Manafeeder Panthara
    "SCH_600": effect_SCH_600_battlecry,  # Demon Companion
    "SCH_312": effect_SCH_312_battlecry,  # Initiation
    "SCH_350": effect_SCH_350_battlecry,  # Wand Thief
    "SCH_313": effect_SCH_313_battlecry,  # Pen Flinger
    "SCH_311": effect_SCH_311_battlecry,  # Animated Broomstick
    "SCH_621": effect_SCH_621_battlecry,  # Raise Dead
    # Spellburst (needs trigger system)
    "SCH_507": effect_SCH_507_spellburst,  # Instructor Fireheart
    "SCH_230": effect_SCH_230_spellburst,  # Onyx Magescribe
    # Triggers
    "SCH_537": effect_SCH_537_trigger,  # Trick Totem
}
