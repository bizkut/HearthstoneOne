from simulator.game import Game

def verify_integration():
    print("Initializing Game...")
    game = Game()
    
    bc_count = len(game._battlecry_handlers)
    dr_count = len(game._deathrattle_handlers)
    print(f"Registered battlecry handlers: {bc_count}")
    print(f"Registered deathrattle handlers: {dr_count}")
    
    # Check key cards from different expansions
    checks = {
        # Battlecries / Spells
        "CS2_029": ("Fireball (Classic)", "battlecry"),
        "GVG_096": ("Piloted Shredder (GVG)", "deathrattle"),
        "BRM_002": ("Flamewaker (BRM)", "trigger"), # Triggers not yet auto-registered
        "LOE_077": ("Brann Bronzebeard (LOE)", "battlecry"), # Actually Brann is an aura/trigger, let's check Reno
        "LOE_011": ("Reno Jackson (LOE)", "battlecry"),
        "OG_280": ("C'Thun (WOG)", "battlecry"),
        "ICC_855": ("Hyldnir Frostrider (ICC)", "battlecry"),
        "LOOT_167": ("Fungalmancer (Kobolds)", "battlecry"),
        "GIL_212": ("Ravencaller (Witchwood)", "battlecry"), 
        "BOT_031": ("Goblin Bomb (Boomsday)", "deathrattle"),
        "TRL_509": ("Banana Buffoon (Rastakhan)", "battlecry"),
        "DAL_735": ("Dalaran Librarian (Dalaran)", "battlecry"),
        "ULD_183": ("Anubisath Warbringer (Uldum)", "deathrattle"),
        "DRG_054": ("Big Ol' Whelp (Dragons)", "battlecry"),
        "BT_726": ("Dragonmaw Sky Stalker (Outlands)", "deathrattle")
    }
    
    success_count = 0
    total_checkable = 0
    
    for card_id, (name, effect_type) in checks.items():
        if effect_type == "trigger":
            # Triggers are known to not be registered yet
            print(f"[SKIP] {name} ({card_id}) - Trigger registration pending")
            continue
            
        total_checkable += 1
        found = False
        
        if effect_type == "battlecry":
            if card_id in game._battlecry_handlers:
                found = True
                print(f"[OK] {name} found in battlecry handlers")
        elif effect_type == "deathrattle":
            if card_id in game._deathrattle_handlers:
                found = True
                print(f"[OK] {name} found in deathrattle handlers")
                
        if found:
            success_count += 1
        else:
            print(f"[FAIL] {name} ({card_id}) MISSING from {effect_type} handlers")

    print(f"\nVerification Result: {success_count}/{total_checkable} checkable effects found")
    
    if success_count == total_checkable:
        print("SUCCESS: All checkable effects verified!")
    else:
        print("WARNING: Some effects missing.")

if __name__ == "__main__":
    verify_integration()
