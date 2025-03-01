import os
import json
import requests
from pathlib import Path

def get_level_name(level_id):
    """Fetch the level name from the server using the provided level ID."""
    url = "http://www.boomlings.com/database/downloadGJLevel22.php"
    headers = {"User-Agent": ""}
    data = {"levelID": level_id, "secret": "Wmfd2893gb7"}
    
    response = requests.post(url, data=data, headers=headers)
    
    if response.status_code == 200:
        level_data = response.text
        level_parts = level_data.split(':')
        return level_parts[3] if len(level_parts) > 3 else None
    else:
        return None

def update_levels_json(level_name, level_id):
    """Update levels.json with the new level name and ID."""
    levels_file = Path('levels.json')
    
    if levels_file.exists():
        with open(levels_file, 'r') as file:
            levels_data = json.load(file)
    else:
        levels_data = {}

    # Add new entry or update if exists
    levels_data[level_name] = level_id

    # Save the updated data back to levels.json
    with open(levels_file, 'w') as file:
        json.dump(levels_data, file, indent=4)
    print(f"Updated levels.json with {level_name}: {level_id}")

def process_uploaded_files():
    """Process all newly added files in the /uploads folder."""
    # Get the commit diff to find added files
    added_files = os.popen("git diff --name-only --diff-filter=A HEAD~1 HEAD").read().splitlines()

    for file in added_files:
        if file.startswith("uploads/") and file.endswith(".gdr2"):
            level_id = int(file.split('/')[1].split('.')[0])  # Extract level id from the file name
            level_name = get_level_name(level_id)

            if level_name:
                print(f"Level Name: {level_name}, Level ID: {level_id}")
                update_levels_json(level_name, level_id)
            else:
                print(f"Failed to fetch level name for ID: {level_id}")

if __name__ == "__main__":
    process_uploaded_files()
