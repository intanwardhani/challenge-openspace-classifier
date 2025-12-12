# UTF-8 Python 3.13.5
# Main runner for Openspace Organisr
# Author: Intan K. Wardhani

import json
import os
from typing import Any, Dict

from src.openspace import OpenSpace
from src.utils import FileManager

# ====== Configuration ======
CONFIG_PATH = "config.json"

# ====== Utility functions ======

def load_config() -> Dict[str, Any] | None:
    """Load configuration from config.json if it exists."""
    if not os.path.exists(CONFIG_PATH):
        print(f"⚠️ Config file not found at {CONFIG_PATH}.")
        return None

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        print("✅ Loaded configuration from config.json")
        return config
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON format in config.json.")
        return None


def get_manual_input() -> Dict[str, Any] | None:
    """Prompt user for manual setup instead of config.json."""
    print("\nManual setup mode:")
    input_file = input("Enter CSV file name (e.g., people.csv): ").strip()
    output_file = input("Enter output file name (default: seating.txt): ").strip() or "seating.txt"
    try:
        number_of_tables = int(input("Enter number of tables: ").strip())
        table_capacity = int(input("Enter table capacity: ").strip())
    except ValueError:
        print("❌ Please enter valid integers for tables and capacity.")
        return None

    return {
        "input_file": input_file,
        "output_file": output_file,
        "number_of_tables": number_of_tables,
        "table_capacity": table_capacity,
        "preferences": {},
    }


def run_organisation(config: Dict[str, Any]) -> None:
    """Run the main seating organisation workflow."""
    # Load people
    people_data = FileManager.from_csv(config["input_file"])
    people = [row["name"] for row in people_data]

    preferences = config.get("preferences", {})

    # Create OpenSpace instance
    open_space = OpenSpace(
        number_of_tables=config["number_of_tables"],
        table_capacity=config["table_capacity"],
    )

    # Organise seating with historical preferences
    open_space.organise(people, preferences=preferences, persistent=True)
    print("\n✅ People have been organised into tables.")

    # Display seating
    seating = open_space.display()
    print("\nSeating arrangement:")
    for table_name, occupants in seating.items():
        occupants_str = ", ".join(occupants) if occupants else "(empty)"
        print(f"  {table_name}: {occupants_str}")

    # Ask user for output format
    file_type = input("Save seating as .txt (default) or .csv? Enter txt/csv: ").strip().lower()
    if file_type not in ["csv", "txt"]:
        file_type = "txt"  # default

    out_file = config["output_file"]

    # Export using FileManager
    if file_type == "csv":
        FileManager.to_csv(people_data, out_file)
        print(f"\n✅ Seating exported to {out_file}")
    else:
        FileManager.to_txt(open_space, preferences, out_file)
        print(f"\n✅ Seating exported to {out_file}")


# ====== Main program loop ======
if __name__ == "__main__":
    config = load_config()
    use_config = "y" if config else "n"

    if use_config != "y":
        config = get_manual_input()
        if not config:
            print("❌ Configuration failed. Exiting.")
            exit(1)

    while True:
        print("\nOptions:")
        print(" 1. Add a person")
        print(" 2. Add a table")
        print(" 3. Add or update a seating preference")
        print(" 4. Reorganise everyone (respecting preferences)")
        if use_config == "y":
            print(" r. Reload config.json (manual refresh)")
        print(" 5. Exit")
        choice = input("Choose an option: ").strip().lower()

        if choice == "1":
            print("⚠️ Feature: Add person not yet implemented in main.py loop.")
        elif choice == "2":
            print("⚠️ Feature: Add table not yet implemented in main.py loop.")
        elif choice == "3":
            print("⚠️ Feature: Add/update preferences not yet implemented in main.py loop.")
        elif choice == "4":
            run_organisation(config)
        elif choice == "r" and use_config == "y":
            config = load_config()
            if not config:
                print("❌ Failed to reload config.json.")
                continue
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("❌ Invalid option, please try again.")

