"""The Witchwood Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS ===

# GIL_118 - Deranged Doctor
def effect_GIL_118_deathrattle(game, source):
    """Deranged Doctor: Deathrattle: Restore 8 Health to your hero."""
    if source.controller.hero:
        game.heal(source.controller.hero, 8)


# GIL_212 - Ravencaller
def effect_GIL_212_battlecry(game, source, target):
    """Ravencaller: Battlecry: Add two random 1-Cost minions to your hand."""
    from simulator.card_loader import CardDatabase, create_card
    from simulator.enums import CardType
    
    db = CardDatabase.get_instance()
    db.load()
    
    one_cost = [
        cid for cid, card in db._cards.items()
        if card.card_type == CardType.MINION and card.cost == 1 and card.collectible
    ]
    for _ in range(2):
        if one_cost:
            minion = create_card(random.choice(one_cost), game)
            source.controller.add_to_hand(minion)


# GIL_213 - Tanglefur Mystic
def effect_GIL_213_battlecry(game, source, target):
    """Tanglefur Mystic: Battlecry: Add a random 2-Cost minion to each player's hand."""
    from simulator.card_loader import CardDatabase, create_card
    from simulator.enums import CardType
    
    db = CardDatabase.get_instance()
    db.load()
    
    two_cost = [
        cid for cid, card in db._cards.items()
        if card.card_type == CardType.MINION and card.cost == 2 and card.collectible
    ]
    for p in game.players:
        if two_cost:
            minion = create_card(random.choice(two_cost), game)
            p.add_to_hand(minion)


# GIL_513 - Lost Spirit
def effect_GIL_513_deathrattle(game, source):
    """Lost Spirit: Deathrattle: Give your minions +1 Attack."""
    for m in source.controller.board:
        m._attack += 1


# GIL_526 - Wyrmguard
def effect_GIL_526_battlecry(game, source, target):
    """Wyrmguard: Battlecry: If you're holding a Dragon, gain +1 Attack and Taunt."""
    from simulator.enums import Race
    holding_dragon = any(getattr(c.data, 'race', None) == Race.DRAGON for c in source.controller.hand)
    if holding_dragon:
        source._attack += 1
        source.taunt = True


# GIL_534 - Hench-Clan Thug
def effect_GIL_534_trigger(game, source, attack_event):
    """Hench-Clan Thug: After your hero attacks, give this minion +1/+1."""
    source._attack += 1
    source._health += 1
    source.max_health += 1


# GIL_667 - Rotten Applebaum
def effect_GIL_667_deathrattle(game, source):
    """Rotten Applebaum: Deathrattle: Restore 4 Health to your hero."""
    if source.controller.hero:
        game.heal(source.controller.hero, 4)


# GIL_683 - Marsh Drake
def effect_GIL_683_battlecry(game, source, target):
    """Marsh Drake: Battlecry: Summon a 2/1 Poisonous Drakeslayer for your opponent."""
    if len(source.controller.opponent.board) < 7:
        game.summon_token(source.controller.opponent, "GIL_683t")


# GIL_816 - Swamp Dragon Egg
def effect_GIL_816_deathrattle(game, source):
    """Swamp Dragon Egg: Deathrattle: Add a random Dragon to your hand."""
    from simulator.card_loader import CardDatabase, create_card
    from simulator.enums import Race
    
    db = CardDatabase.get_instance()
    db.load()
    
    dragons = [
        cid for cid, card in db._cards.items()
        if getattr(card, 'race', None) == Race.DRAGON and card.collectible
    ]
    if dragons:
        dragon = create_card(random.choice(dragons), game)
        source.controller.add_to_hand(dragon)


# Registry
WITCHWOOD_EFFECTS = {
    # Battlecries
    "GIL_212": effect_GIL_212_battlecry,
    "GIL_213": effect_GIL_213_battlecry,
    "GIL_526": effect_GIL_526_battlecry,
    "GIL_683": effect_GIL_683_battlecry,
    # Deathrattles
    "GIL_118": effect_GIL_118_deathrattle,
    "GIL_513": effect_GIL_513_deathrattle,
    "GIL_667": effect_GIL_667_deathrattle,
    "GIL_816": effect_GIL_816_deathrattle,
    # Triggers
    "GIL_534": effect_GIL_534_trigger,
}
