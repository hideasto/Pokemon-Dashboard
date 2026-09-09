import requests
import time
import csv
import json
import os
import sys

# ============================================
# YOUR SAVE LOCATION
# ============================================
SAVE_FOLDER = r"C:\Users\User\Desktop\Github Codes\Pokemon Dashboard\pokeapi data"

# Create folder if it doesn't exist
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)
    print(f"📁 Created folder: {SAVE_FOLDER}")

# ============================================
# MAPPING: Game -> Version Group (for movesets)
# ============================================
GAME_TO_VERSION_GROUP = {
    # Generation 1
    "red": "red-blue",
    "blue": "red-blue",
    "yellow": "red-blue",
    # Generation 2
    "gold": "gold-silver",
    "silver": "gold-silver",
    "crystal": "gold-silver",
    # Generation 3
    "ruby": "ruby-sapphire",
    "sapphire": "ruby-sapphire",
    "emerald": "ruby-sapphire",
    "firered": "firered-leafgreen",
    "leafgreen": "firered-leafgreen",
    # Generation 4
    "diamond": "diamond-pearl",
    "pearl": "diamond-pearl",
    "platinum": "diamond-pearl",
    "heartgold": "heartgold-soulsilver",
    "soulsilver": "heartgold-soulsilver",
    # Generation 5
    "black": "black-white",
    "white": "black-white",
    "black-2": "black-2-white-2",
    "white-2": "black-2-white-2",
    # Generation 6
    "x": "x-y",
    "y": "x-y",
    "omega-ruby": "omega-ruby-alpha-sapphire",
    "alpha-sapphire": "omega-ruby-alpha-sapphire",
    # Generation 7
    "sun": "sun-moon",
    "moon": "sun-moon",
    "ultra-sun": "ultra-sun-ultra-moon",
    "ultra-moon": "ultra-sun-ultra-moon",
    # Generation 8
    "sword": "sword-shield",
    "shield": "sword-shield",
    # Generation 9
    "scarlet": "scarlet-violet",
    "violet": "scarlet-violet",
}

# All games to include (ordered by generation)
ALL_GAMES = [
    # Gen 1
    "red", "blue", "yellow",
    # Gen 2
    "gold", "silver", "crystal",
    # Gen 3
    "ruby", "sapphire", "emerald", "firered", "leafgreen",
    # Gen 4
    "diamond", "pearl", "platinum", "heartgold", "soulsilver",
    # Gen 5
    "black", "white", "black-2", "white-2",
    # Gen 6
    "x", "y", "omega-ruby", "alpha-sapphire",
    # Gen 7
    "sun", "moon", "ultra-sun", "ultra-moon",
    # Gen 8
    "sword", "shield",
    # Gen 9
    "scarlet", "violet"
]

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

def get_pokemon_encounters(name):
    """Get encounter locations and levels"""
    url = f"https://pokeapi.co/api/v2/pokemon/{name}/encounters"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        return []

def get_pokemon_moves_for_version(name, version_group):
    """Get level-up moves for a specific version group"""
    url = f"https://pokeapi.co/api/v2/pokemon/{name}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            moves = []
            for move_entry in data['moves']:
                for version_detail in move_entry['version_group_details']:
                    if (version_detail['move_learn_method']['name'] == 'level-up' and 
                        version_detail['version_group']['name'] == version_group):
                        moves.append({
                            'move': move_entry['move']['name'],
                            'level_learned': version_detail['level_learned_at']
                        })
            moves.sort(key=lambda x: x['level_learned'])
            return moves
        return []
    except Exception as e:
        return []

def get_moves_at_level(moves, level):
    """Get the last 4 moves learned up to a level"""
    known = [m['move'] for m in moves if m['level_learned'] <= level]
    return known[-4:] if len(known) >= 4 else known

def get_generation_from_game(game_name):
    """Return the generation number for a game"""
    gen_map = {
        "red": 1, "blue": 1, "yellow": 1,
        "gold": 2, "silver": 2, "crystal": 2,
        "ruby": 3, "sapphire": 3, "emerald": 3, "firered": 3, "leafgreen": 3,
        "diamond": 4, "pearl": 4, "platinum": 4, "heartgold": 4, "soulsilver": 4,
        "black": 5, "white": 5, "black-2": 5, "white-2": 5,
        "x": 6, "y": 6, "omega-ruby": 6, "alpha-sapphire": 6,
        "sun": 7, "moon": 7, "ultra-sun": 7, "ultra-moon": 7,
        "sword": 8, "shield": 8,
        "scarlet": 9, "violet": 9
    }
    return gen_map.get(game_name, 0)

# ============================================
# MAIN SCRIPT
# ============================================
def main():
    print("\n" + "="*70)
    print("🎮 POKEMON DATA COLLECTOR - ALL GENERATIONS")
    print("="*70)
    print(f"📁 Save Location: {SAVE_FOLDER}")
    print(f"📌 Games: {len(ALL_GAMES)} games across 9 generations")
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
    total_pokemon = len(all_pokemon)
    
    print(f"\n🔄 Processing {total_pokemon} Pokémon across {len(ALL_GAMES)} games...")
    print("⏱️ This will take a while. Estimated time: ~1-2 hours for all Pokémon")
    print("💡 Tip: Start with 10-20 Pokémon for a quick test!\n")
    
    # Track stats
    total_encounters = 0
    pokemon_with_encounters = 0
    
    for i, pokemon_name in enumerate(all_pokemon):
        print(f"  [{i+1}/{total_pokemon}] {pokemon_name}...", end="")
        
        # Get encounter data
        encounters = get_pokemon_encounters(pokemon_name)
        
        if not encounters:
            print(" ⚠️ No encounters found (legendary/gift)")
            continue
        
        # Track Pokémon with encounters
        pokemon_with_encounters += 1
        encounter_count = 0
        
        # Process each encounter
        for location_data in encounters:
            location_name = location_data['location_area']['name']
            
            for version_detail in location_data['version_details']:
                game_name = version_detail['version']['name']
                
                # Check if this game is in our list
                if game_name not in ALL_GAMES:
                    continue
                
                # Get the version group for moveset
                version_group = GAME_TO_VERSION_GROUP.get(game_name, "red-blue")
                generation = get_generation_from_game(game_name)
                
                # Get moveset for this version group
                moves = get_pokemon_moves_for_version(pokemon_name, version_group)
                
                for encounter in version_detail['encounter_details']:
                    min_level = encounter['min_level']
                    max_level = encounter['max_level']
                    method = encounter['method']['name']
                    
                    # Get moves at this level
                    moves_at_level = get_moves_at_level(moves, min_level)
                    moves_str = ', '.join(moves_at_level) if moves_at_level else 'None'
                    
                    all_data.append({
                        'pokemon': pokemon_name,
                        'generation': generation,
                        'game': game_name,
                        'location': location_name,
                        'min_level': min_level,
                        'max_level': max_level,
                        'method': method,
                        'moves': moves_str
                    })
                    encounter_count += 1
                    total_encounters += 1
        
        print(f" ✅ {encounter_count} encounters found")
        
        # Be nice to the API
        time.sleep(0.3)
    
    # ============================================
    # SAVE DATA
    # ============================================
    if all_data:
        # Sort by generation then Pokémon
        all_data.sort(key=lambda x: (x['generation'], x['pokemon']))
        
        # Save CSV
        csv_path = os.path.join(SAVE_FOLDER, "pokemon_all_generations_data.csv")
        json_path = os.path.join(SAVE_FOLDER, "pokemon_all_generations_data.json")
        
        print(f"\n💾 Saving to: {csv_path}")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['pokemon', 'generation', 'game', 'location', 'min_level', 'max_level', 'method', 'moves']
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
        print(f"📊 Total encounters: {len(all_data)}")
        print(f"📊 Pokémon with encounters: {pokemon_with_encounters}/{total_pokemon}")
        print(f"📊 Games covered: {len(ALL_GAMES)}")
        print(f"📊 Generations covered: 1-9")
        print(f"📁 CSV: {csv_path}")
        print(f"📁 JSON: {json_path}")
        
        # Show preview by generation
        print("\n📋 Preview by Generation:")
        print("-" * 70)
        gen_counts = {}
        for row in all_data:
            gen = row['generation']
            gen_counts[gen] = gen_counts.get(gen, 0) + 1
        
        for gen in sorted(gen_counts.keys()):
            print(f"  Gen {gen}: {gen_counts[gen]} entries")
        
        # Show sample rows
        print("\n📋 Sample Data (first 5 entries):")
        print("-" * 70)
        for i, row in enumerate(all_data[:5]):
            print(f"{i+1}. {row['pokemon']} | Gen{row['generation']} | {row['game']} | {row['location']} | Lv.{row['min_level']}-{row['max_level']} | {row['moves']}")
        if len(all_data) > 5:
            print(f"... and {len(all_data) - 5} more entries")
        print("-" * 70)
        
        print("\n🎉 Open the CSV file in Excel or Google Sheets!")
    else:
        print("\n❌ No data collected.")
    
    input("\n✅ Press Enter to close this window...")

if __name__ == "__main__":
    main()
