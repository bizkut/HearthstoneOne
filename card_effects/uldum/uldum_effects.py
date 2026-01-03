"""Saviors of Uldum Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS ===

# ULD_174 - Serpent Egg
def effect_ULD_174_deathrattle(game, source):
    """Serpent Egg: Deathrattle: Summon a 3/4 Sea Serpent."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "ULD_174t")


# ULD_182 - Spitting Camel
def effect_ULD_182_trigger(game, source, turn_end):
    """Spitting Camel: At the end of your turn, deal 1 damage to another random friendly minion."""
    others = [m for m in source.controller.board if m != source]
    if others:
        game.deal_damage(random.choice(others), 1)


# ULD_183 - Anubisath Warbringer
def effect_ULD_183_deathrattle(game, source):
    """Anubisath Warbringer: Deathrattle: Give all minions in your hand +3/+3."""
    from simulator.enums import CardType
    for card in source.controller.hand:
        if card.data.card_type == CardType.MINION:
            card._attack = getattr(card, '_attack', card.data.attack) + 3
            card._health = getattr(card, '_health', card.data.health) + 3


# ULD_184 - Kobold Sandtrooper
def effect_ULD_184_deathrattle(game, source):
    """Kobold Sandtrooper: Deathrattle: Deal 3 damage to the enemy hero."""
    if source.controller.opponent.hero:
        game.deal_damage(source.controller.opponent.hero, 3)


# ULD_189 - Faceless Lurker
def effect_ULD_189_battlecry(game, source, target):
    """Faceless Lurker: Battlecry: Double this minion's Health."""
    source._health *= 2
    source.max_health *= 2


# ULD_190 - Pit Crocolisk
def effect_ULD_190_battlecry(game, source, target):
    """Pit Crocolisk: Battlecry: Deal 5 damage."""
    if target:
        game.deal_damage(target, 5)


# ULD_191 - Beaming Sidekick
def effect_ULD_191_battlecry(game, source, target):
    """Beaming Sidekick: Battlecry: Give a friendly minion +2 Health."""
    if target and target.controller == source.controller:
        target._health += 2
        target.max_health += 2


# ULD_271 - Injured Tol'vir
def effect_ULD_271_battlecry(game, source, target):
    """Injured Tol'vir: Battlecry: Deal 3 damage to this minion."""
    game.deal_damage(source, 3)


# ULD_282 - Jar Dealer
def effect_ULD_282_deathrattle(game, source):
    """Jar Dealer: Deathrattle: Add a random 1-Cost minion to your hand."""
    from simulator.card_loader import CardDatabase, create_card
    from simulator.enums import CardType
    
    db = CardDatabase.get_instance()
    db.load()
    
    one_cost = [
        cid for cid, card in db._cards.items()
        if card.card_type == CardType.MINION and card.cost == 1 and card.collectible
    ]
    if one_cost:
        minion = create_card(random.choice(one_cost), game)
        source.controller.add_to_hand(minion)


# ULD_712 - Bug Collector
def effect_ULD_712_battlecry(game, source, target):
    """Bug Collector: Battlecry: Summon a 1/1 Locust with Rush."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "ULD_430t")


# ULD_719 - Desert Hare
def effect_ULD_719_battlecry(game, source, target):
    """Desert Hare: Battlecry: Summon two 1/1 Desert Hares."""
    for _ in range(2):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "ULD_719")


# Registry
ULDUM_EFFECTS = {
    # Deathrattles
    "ULD_174": effect_ULD_174_deathrattle,
    "ULD_183": effect_ULD_183_deathrattle,
    "ULD_184": effect_ULD_184_deathrattle,
    "ULD_282": effect_ULD_282_deathrattle,
    # Battlecries
    "ULD_189": effect_ULD_189_battlecry,
    "ULD_190": effect_ULD_190_battlecry,
    "ULD_191": effect_ULD_191_battlecry,
    "ULD_271": effect_ULD_271_battlecry,
    "ULD_712": effect_ULD_712_battlecry,
    "ULD_719": effect_ULD_719_battlecry,
    # Triggers
    "ULD_182": effect_ULD_182_trigger,
}
