# UTF-8 Python 3.13.5
# Main runner for Openspace Organisr
# Author: Intan K. Wardhani

import json
import os
from typing import Any, Dict

from src.openspace import OpenSpace
from src.utils import FileManager
from src.table import Table
from src.snapshot import SeatingSnapshot

# ---------- Configuration ----------
CONFIG_PATH = "config.json"

# ---------- Utility functions ----------
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

    preferences = {}
    while True:
        add_preferences = input("Do you want to add seating preferences for a person? (y/n): ").strip().lower()
        if add_preferences == "y":
            name = input("Enter the person's name: ").strip()
            with_list = input(f"Enter people {name} wants to sit with (comma-separated): ").strip().split(",")
            without_list = input(f"Enter people {name} doesn't want to sit with (comma-separated): ").strip().split(",")
            preferences[name] = {
                "with": [p.strip() for p in with_list],
                "without": [p.strip() for p in without_list],
            }
        elif add_preferences == "n":
            break
        else:
            print("❌ Invalid option, please try again.")

    return {
        "input_file": input_file,
        "output_file": output_file,
        "number_of_tables": number_of_tables,
        "table_capacity": table_capacity,
        "preferences": preferences,
    }


def run_organisation(config: Dict[str, Any]) -> None:
    """Run the main seating organisation workflow."""

    # ---------- Load people ----------
    people_data = FileManager.from_csv(config["input_file"])
    people = [row['name'] for row in people_data]

    preferences = config.get("preferences", {})

    # ---------- Create tables ----------
    tables = [
        Table(f"Table {i + 1}", config["table_capacity"])
        for i in range(config["number_of_tables"])
            ]

    # ---------- Organise seating ----------
    open_space = OpenSpace(people=people, tables=tables, config=config)
    open_space.organise(preferences=preferences, persistent=True)

    print("\n✅ People have been organised into tables.")

    # ---------- Visual display (decorative only) ----------
    seating = open_space.display()
    print("\nSeating arrangement:")
    for table_name, occupants in seating.items():
        occupants_str = ", ".join(occupants) if occupants else "(empty)"
        print(f"  {table_name}: {occupants_str}")

    # ---------- Build snapshot (single source of truth) ----------
    snapshot = SeatingSnapshot(open_space, preferences)

    # ---------- Ask output format ----------
    file_type = input(
        "Save seating as .txt (default) or .csv? Enter txt/csv: "
    ).strip().lower()

    if file_type not in ("csv", "txt"):
        file_type = "txt"

    out_file = config["output_file"]

    # ---------- Export ----------
    if file_type == "csv":
        FileManager.to_csv(snapshot.rows(), out_file)
        print(f"\n✅ Seating exported to {out_file}")
    else:
        FileManager.to_txt(snapshot, out_file)
        print(f"\n✅ Seating exported to {out_file}")


# ---------- Main program loop ----------
if __name__ == "__main__":
    config = load_config()

    if not config:
        print("\nConfig.json not found. Proceeding with manual input.")
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
        print(" 5. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            print("⚠️ Feature not yet implemented.")
        elif choice == "2":
            print("⚠️ Feature not yet implemented.")
        elif choice == "3":
            print("⚠️ Feature not yet implemented.")
        elif choice == "4":
            run_organisation(config)
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("❌ Invalid option, please try again.")

