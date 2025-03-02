import os
import json
import requests
from pathlib import Path
from glob import glob

LEVELS_FILE = Path("levels.json")
UPLOADS_FOLDER = Path("uploads")

def load_levels():
    """Load existing levels from levels.json, or return an empty dict if the file doesn't exist or is corrupted."""
    if LEVELS_FILE.exists():
        with open(LEVELS_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}  # Return empty dict if JSON is corrupted
    return {}

def get_uploaded_level_ids():
    """Get all level IDs from the uploads folder (filenames in uploads/*.gdr2)."""
    level_ids = set()
    for file in glob(str(UPLOADS_FOLDER / "*.gdr2")):
        try:
            level_id = int(Path(file).stem)
            level_ids.add(str(level_id))  # Store as string for consistency
        except ValueError:
            print(f"Skipping invalid filename: {file}")
    return level_ids

def get_level_name(level_id):
    """Fetch the level name from the server using the provided level ID."""
    url = "https://www.boomlings.com/database/downloadGJLevel22.php"
    headers = {"User-Agent": ""}
    data = {"levelID": level_id, "secret": "Wmfd2893gb7"}

    print("\n--- Making Request ---")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {data}")

    response = requests.post(url, data=data, headers=headers)

    print(f"Response Code: {response.status_code}")
    print(f"Response Text: {response.text[:500]}")  # Print first 500 chars of response

    if response.status_code == 200:
        level_parts = response.text.split(":")
        return level_parts[3] if len(level_parts) > 3 else None
    return None

def sync_levels():
    """Ensure levels.json and uploads/ match, updating/removing entries as needed."""
    levels_data = load_levels()
    uploaded_ids = get_uploaded_level_ids()

    # Convert levels.json to { "LevelID": "LevelName" } for easier comparison
    levels_by_id = {v: k for k, v in levels_data.items()}

    # Find discrepancies
    json_ids = set(levels_by_id.keys())
    missing_from_json = uploaded_ids - json_ids  # Levels in uploads/ but not in json
    missing_from_uploads = json_ids - uploaded_ids  # Levels in json but not in uploads/

    # Remove missing_from_uploads from json
    for level_id in missing_from_uploads:
        level_name = levels_by_id[level_id]
        print(f"Removing {level_name} (ID: {level_id}) from levels.json (not found in uploads/)")
        del levels_data[level_name]

    # Fetch and add missing levels to json
    for level_id in missing_from_json:
        level_name = get_level_name(level_id)
        if level_name:
            print(f"Adding {level_name} (ID: {level_id}) to levels.json")
            levels_data[level_name] = level_id
        else:
            print(f"Failed to fetch level name for ID: {level_id}")

    # Save the updated levels.json
    with open(LEVELS_FILE, "w") as file:
        json.dump(levels_data, file, indent=4)

    print("levels.json successfully synced with uploads/.")

if __name__ == "__main__":
    sync_levels()
