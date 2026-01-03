"""League of Explorers Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS ===

# LOE_011 - Reno Jackson
def effect_LOE_011_battlecry(game, source, target):
    """Reno Jackson: Battlecry: If your deck has no duplicates, fully heal your hero."""
    deck_ids = [c.card_id for c in source.controller.deck]
    has_duplicates = len(deck_ids) != len(set(deck_ids))
    if not has_duplicates and source.controller.hero:
        source.controller.hero.health = source.controller.hero.max_health


# LOE_012 - Tomb Pillager
def effect_LOE_012_deathrattle(game, source):
    """Tomb Pillager: Deathrattle: Add a Coin to your hand."""
    from simulator.card_loader import create_card
    coin = create_card("GAME_005", game)
    source.controller.add_to_hand(coin)


# LOE_017 - Keeper of Uldaman
def effect_LOE_017_battlecry(game, source, target):
    """Keeper of Uldaman: Battlecry: Set a minion's Attack and Health to 3."""
    if target:
        target._attack = 3
        target._health = 3
        target.max_health = 3


# LOE_018 - Tunnel Trogg
def effect_LOE_018_trigger(game, source, overload_event):
    """Tunnel Trogg: Whenever you Overload, gain +1 Attack for each locked Mana Crystal."""
    overload_amount = getattr(overload_event, 'amount', 1)
    source._attack += overload_amount


# LOE_046 - Huge Toad
def effect_LOE_046_deathrattle(game, source):
    """Huge Toad: Deathrattle: Deal 1 damage to a random enemy."""
    targets = list(source.controller.opponent.board) + [source.controller.opponent.hero]
    targets = [t for t in targets if t and getattr(t, 'health', 1) > 0]
    if targets:
        game.deal_damage(random.choice(targets), 1)


# LOE_050 - Mounted Raptor
def effect_LOE_050_deathrattle(game, source):
    """Mounted Raptor: Deathrattle: Summon a random 1-Cost minion."""
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


# LOE_061 - Anubisath Sentinel
def effect_LOE_061_deathrattle(game, source):
    """Anubisath Sentinel: Deathrattle: Give a random friendly minion +3/+3."""
    others = [m for m in source.controller.board if m != source]
    if others:
        target_minion = random.choice(others)
        target_minion._attack += 3
        target_minion._health += 3
        target_minion.max_health += 3


# LOE_077 - Brann Bronzebeard
# (Aura effect - doubles battlecries, handled by game engine)


# LOE_089 - Wobbling Runts
def effect_LOE_089_deathrattle(game, source):
    """Wobbling Runts: Deathrattle: Summon three 2/2 Runts."""
    tokens = ["LOE_089t", "LOE_089t2", "LOE_089t3"]
    for token_id in tokens:
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, token_id)


# LOE_110 - Ancient Shade
def effect_LOE_110_battlecry(game, source, target):
    """Ancient Shade: Battlecry: Shuffle an 'Ancient Curse' into your deck that deals 7 damage to you when drawn."""
    from simulator.card_loader import create_card
    curse = create_card("LOE_110t", game)
    source.controller.deck.append(curse)
    random.shuffle(source.controller.deck)


# === SPELLS ===

# LOE_002 - Forgotten Torch
def effect_LOE_002_battlecry(game, source, target):
    """Forgotten Torch: Deal 3 damage. Shuffle a 6-damage Roaring Torch into your deck."""
    if target:
        game.deal_damage(target, 3)
    from simulator.card_loader import create_card
    torch = create_card("LOE_002t", game)
    source.controller.deck.append(torch)
    random.shuffle(source.controller.deck)


# LOE_002t - Roaring Torch
def effect_LOE_002t_battlecry(game, source, target):
    """Roaring Torch: Deal 6 damage."""
    if target:
        game.deal_damage(target, 6)


# LOE_007 - Curse of Rafaam
def effect_LOE_007_battlecry(game, source, target):
    """Curse of Rafaam: Give your opponent a 'Cursed!' card that deals 2 damage to them at start of turn."""
    from simulator.card_loader import create_card
    curse = create_card("LOE_007t", game)
    source.controller.opponent.add_to_hand(curse)


# LOE_026 - Anyfin Can Happen
def effect_LOE_026_battlecry(game, source, target):
    """Anyfin Can Happen: Summon 7 Murlocs that died this game."""
    from simulator.enums import Race
    dead_murlocs = [cid for cid in getattr(game, 'graveyard', []) 
                    if getattr(source.controller.deck, 'race', None) == Race.MURLOC]
    # Simplified: summon up to 7 murloc tokens
    pass


# LOE_104 - Entomb
def effect_LOE_104_battlecry(game, source, target):
    """Entomb: Choose an enemy minion. Shuffle it into your deck."""
    if target and target.controller == source.controller.opponent:
        # Remove from board
        if target in target.controller.board:
            target.controller.board.remove(target)
        # Add to deck
        source.controller.deck.append(target)
        random.shuffle(source.controller.deck)


# LOE_111 - Excavated Evil
def effect_LOE_111_battlecry(game, source, target):
    """Excavated Evil: Deal 3 damage to all minions. Shuffle this card into your opponent's deck."""
    for p in game.players:
        for m in p.board[:]:
            game.deal_damage(m, 3)
    from simulator.card_loader import create_card
    copy = create_card("LOE_111", game)
    source.controller.opponent.deck.append(copy)
    random.shuffle(source.controller.opponent.deck)


# LOE_113 - Everyfin is Awesome
def effect_LOE_113_battlecry(game, source, target):
    """Everyfin is Awesome: Give your minions +2/+2. Costs (1) less for each Murloc you control."""
    for m in source.controller.board:
        m._attack += 2
        m._health += 2
        m.max_health += 2


# Registry
LOE_EFFECTS = {
    # Battlecries
    "LOE_011": effect_LOE_011_battlecry,
    "LOE_017": effect_LOE_017_battlecry,
    "LOE_110": effect_LOE_110_battlecry,
    # Deathrattles
    "LOE_012": effect_LOE_012_deathrattle,
    "LOE_046": effect_LOE_046_deathrattle,
    "LOE_050": effect_LOE_050_deathrattle,
    "LOE_061": effect_LOE_061_deathrattle,
    "LOE_089": effect_LOE_089_deathrattle,
    # Triggers
    "LOE_018": effect_LOE_018_trigger,
    # Spells
    "LOE_002": effect_LOE_002_battlecry,
    "LOE_002t": effect_LOE_002t_battlecry,
    "LOE_007": effect_LOE_007_battlecry,
    "LOE_104": effect_LOE_104_battlecry,
    "LOE_111": effect_LOE_111_battlecry,
    "LOE_113": effect_LOE_113_battlecry,
}
