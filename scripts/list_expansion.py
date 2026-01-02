from simulator import CardDatabase

def list_cards_to_implement(card_set):
    CardDatabase.get_instance().load()
    cards = [c for c in CardDatabase.get_collectible_cards() 
             if c.card_set == card_set and (c.text or c.battlecry or c.deathrattle)]
    
    for c in cards:
        print(f"{c.card_id} | {c.name} | {c.text}")

if __name__ == "__main__":
    import sys
    card_set = sys.argv[1] if len(sys.argv) > 1 else "CORE"
    list_cards_to_implement(card_set)
