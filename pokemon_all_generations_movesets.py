import requests
import time
import csv
import json
import os

# ============================================
# YOUR SAVE LOCATION
# ============================================
SAVE_FOLDER = r"C:\Users\User\Desktop\Github Codes\Pokemon Dashboard\pokeapi data"

# Create folder if it doesn't exist
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)
    print(f"📁 Created folder: {SAVE_FOLDER}")

# ============================================
# CONFIGURATION - ALL VERSION GROUPS
# ============================================
VERSION_GROUPS = [
    # Generation 1
    "red-blue",
    # Generation 2
    "gold-silver", "crystal",
    # Generation 3
    "ruby-sapphire", "emerald", "firered-leafgreen",
    # Generation 4
    "diamond-pearl", "platinum", "heartgold-soulsilver",
    # Generation 5
    "black-white", "black-2-white-2",
    # Generation 6
    "x-y", "omega-ruby-alpha-sapphire",
    # Generation 7
    "sun-moon", "ultra-sun-ultra-moon",
    # Generation 8
    "sword-shield",
    # Generation 9
    "scarlet-violet"
]

# Mapping version group to generation number
VERSION_TO_GEN = {
    "red-blue": 1,
    "gold-silver": 2, "crystal": 2,
    "ruby-sapphire": 3, "emerald": 3, "firered-leafgreen": 3,
    "diamond-pearl": 4, "platinum": 4, "heartgold-soulsilver": 4,
    "black-white": 5, "black-2-white-2": 5,
    "x-y": 6, "omega-ruby-alpha-sapphire": 6,
    "sun-moon": 7, "ultra-sun-ultra-moon": 7,
    "sword-shield": 8,
    "scarlet-violet": 9
}

# ============================================
# FUNCTIONS
# ============================================
def get_all_pokemon_names():
    """Get list of all Pokémon names"""
    print("📡 Fetching Pokémon list...")
    url = "https://pokeapi.co/api/v2/pokemon?limit=1000"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            names = [p['name'] for p in data['results']]
            print(f"✅ Found {len(names)} Pokémon")
            return names
        return []
    except Exception as e:
        print(f"❌ Error fetching list: {e}")
        return []

def get_pokemon_all_moves(pokemon_name):
    """
    Get ALL level-up moves for a Pokémon across ALL version groups
    """
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            all_moves = []
            
            for move_entry in data['moves']:
                for version_detail in move_entry['version_group_details']:
                    # Only get level-up moves
                    if version_detail['move_learn_method']['name'] == 'level-up':
                        version_group = version_detail['version_group']['name']
                        # Only include version groups we're tracking
                        if version_group in VERSION_GROUPS:
                            all_moves.append({
                                'move': move_entry['move']['name'],
                                'level_learned': version_detail['level_learned_at'],
                                'version_group': version_group,
                                'generation': VERSION_TO_GEN.get(version_group, 0)
                            })
            
            # Sort by generation, then Pokémon, then level
            all_moves.sort(key=lambda x: (x['generation'], x['level_learned']))
            return all_moves
        return []
    except Exception as e:
        print(f"  ⚠️ Error getting moves for {pokemon_name}: {e}")
        return []

# ============================================
# MAIN SCRIPT
# ============================================
def main():
    print("\n" + "="*70)
    print("🎮 POKEMON MOVESETS - ALL GENERATIONS")
    print("="*70)
    print(f"📁 Save Location: {SAVE_FOLDER}")
    print(f"📌 Version Groups: {len(VERSION_GROUPS)} across 9 generations")
    print("="*70)
    
    # Ask how many Pokémon to test
    test_input = input("\n👉 How many Pokémon to test? (10 for test, Enter for ALL): ")
    test_limit = None if test_input.strip() == "" else int(test_input)
    
    # Get all Pokémon
    all_pokemon = get_all_pokemon_names()
    
    if not all_pokemon:
        print("❌ Failed to fetch Pokémon. Check your internet connection.")
        input("\nPress Enter to close...")
        return
    
    if test_limit:
        all_pokemon = all_pokemon[:test_limit]
        print(f"🧪 Testing with {len(all_pokemon)} Pokémon")
    
    all_data = []
    total = len(all_pokemon)
    
    print(f"\n🔄 Processing {total} Pokémon across {len(VERSION_GROUPS)} version groups...")
    print("⏱️ This will take a while for all Pokémon. Start with 10 for a quick test!\n")
    
    for i, pokemon_name in enumerate(all_pokemon):
        print(f"  [{i+1}/{total}] {pokemon_name}...", end="")
        
        # Get all moves for this Pokémon
        moves = get_pokemon_all_moves(pokemon_name)
        
        if moves:
            # Add each move as a separate row
            for move in moves:
                all_data.append({
                    'pokemon': pokemon_name,
                    'generation': move['generation'],
                    'version_group': move['version_group'],
                    'move': move['move'],
                    'level_learned': move['level_learned']
                })
            print(f" ✅ {len(moves)} moves found")
        else:
            print(" ⚠️ No moves found")
        
        # Be nice to the API
        time.sleep(0.3)
    
    # ============================================
    # SAVE DATA
    # ============================================
    if all_data:
        # Sort by generation, then Pokémon, then level
        all_data.sort(key=lambda x: (x['generation'], x['pokemon'], x['level_learned']))
        
        # Save CSV
        csv_path = os.path.join(SAVE_FOLDER, "pokemon_all_generations_movesets.csv")
        json_path = os.path.join(SAVE_FOLDER, "pokemon_all_generations_movesets.json")
        
        print(f"\n💾 Saving to: {csv_path}")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['pokemon', 'generation', 'version_group', 'move', 'level_learned']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_data)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2)
        
        # ============================================
        # SUMMARY
        # ============================================
        print("\n" + "="*70)
        print("✅ DATA COLLECTION COMPLETE!")
        print("="*70)
        print(f"📊 Total entries: {len(all_data)}")
        print(f"📁 CSV: {csv_path}")
        print(f"📁 JSON: {json_path}")
        
        # Show stats by generation
        print("\n📋 Stats by Generation:")
        print("-" * 70)
        gen_counts = {}
        for row in all_data:
            gen = row['generation']
            gen_counts[gen] = gen_counts.get(gen, 0) + 1
        
        for gen in sorted(gen_counts.keys()):
            print(f"  Gen {gen}: {gen_counts[gen]} moves")
        
        # Show a preview
        print("\n📋 Preview of data (first 15 entries):")
        print("-" * 70)
        for i, row in enumerate(all_data[:15]):
            print(f"{i+1}. Gen{row['generation']} | {row['pokemon']} | Level {row['level_learned']}: {row['move']}")
        if len(all_data) > 15:
            print(f"... and {len(all_data) - 15} more entries")
        print("-" * 70)
        
        print("\n🎉 Open the CSV file in Excel or Google Sheets!")
    else:
        print("\n❌ No data collected.")
    
    input("\n✅ Press Enter to close this window...")

if __name__ == "__main__":
    main()