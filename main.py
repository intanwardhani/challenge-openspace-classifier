# UTF-8 Python 3.13.5
# Main function to run the utility sources
# Author: Intan K. Wardhani

import json
import os
from typing import Any, Dict, Tuple

from src.openspace import OpenSpace
from src.utils import FileManager


# ====== Configuration ======
CONFIG_PATH = "config.json"


# ====== Utility functions ======
def load_config() -> Dict[str, Any] | None:
    """Load configuration from config.json if it exists."""
    if not os.path.exists(CONFIG_PATH):
        print(f"⚠️  Config file not found at {CONFIG_PATH}.")
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
    print("\n📝 Manual setup mode:")
    input_file = input("Enter CSV file name (e.g., people.csv): ").strip()
    output_file = input("Enter output CSV file name (default: seating.csv): ").strip() or "seating.csv"

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


def run_organisation(config: Dict[str, Any]) -> Tuple[OpenSpace | None, Dict[str, Dict[str, list[str]]]]:
    """Run the full organisation workflow and return OpenSpace + preferences."""
    preferences: Dict[str, Dict[str, list[str]]] = config.get("preferences") or {}

    try:
        people = FileManager.import_csv(config["input_file"])
        print(f"\n✅ Imported {len(people)} people from {config['input_file']}.")
    except FileNotFoundError:
        print(f"❌ Error: File '{config['input_file']}' not found.")
        return None, preferences
    except Exception as e:
        print(f"❌ Error importing CSV: {e}")
        return None, preferences

    open_space = OpenSpace(
        number_of_tables=config["number_of_tables"],
        capacity=config["table_capacity"],
    )

    open_space.organise(people, preferences=preferences, persistent=True)
    print("\n✅ People have been organised into tables.")

    seating = open_space.display()
    print("\nSeating arrangement:")
    for table_name, occupants in seating.items():
        occupants_str = ", ".join(occupants) if occupants else "(empty)"
        print(f"  {table_name}: {occupants_str}")

    open_space.store(config["output_file"])
    print(f"\n💾 Seating arrangement exported to {config['output_file']}")

    return open_space, preferences


def save_preferences_to_config(preferences: Dict[str, Dict[str, list[str]]]) -> None:
    """Safely update the preferences section in config.json."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    config["preferences"] = preferences

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    print("💾 Preferences saved to config.json")


# ====== Main program ======
def main() -> None:
    print("🏢 OpenSpace Table Assignment Program\n")

    # --- Choose input mode ---
    use_config = input("Would you like to load settings from config.json? (y/n): ").strip().lower()
    config: Dict[str, Any] | None = load_config() if use_config == "y" else get_manual_input()

    if not config:
        print("❌ Could not load configuration. Exiting.")
        return

    open_space: OpenSpace | None = None
    preferences: Dict[str, Dict[str, list[str]]] = {}
    open_space, preferences = run_organisation(config)

    if open_space is None:
        print("⚠️ Could not start OpenSpace (check your CSV). Exiting.")
        return

    last_modified: float | None = os.path.getmtime(CONFIG_PATH) if use_config == "y" else None

    # --- Interactive menu loop ---
    while True:
        print("\nOptions:")
        print("  1. Add a person")
        print("  2. Add a table")
        print("  3. Add or update a seating preference")
        print("  4. Reorganise everyone (respecting preferences)")
        if use_config == "y":
            print("  r. Reload config.json (manual refresh)")
        print("  5. Exit")

        choice = input("Choose an option: ").strip().lower()

        # --- Automatic config reload detection ---
        if use_config == "y" and os.path.exists(CONFIG_PATH):
            current_mtime = os.path.getmtime(CONFIG_PATH)
            if last_modified is not None and current_mtime != last_modified:
                print("\n🔁 Detected changes in config.json — reloading...")
                new_config = load_config()
                if new_config is not None:
                    config = new_config
                    open_space, preferences = run_organisation(config)
                    if open_space is None:
                        continue
                    last_modified = current_mtime
                    continue
                else:
                    print("⚠️ Could not reload config.json (invalid format).")
                    continue

        # --- Menu actions ---
        if choice == "1":
            if open_space is not None:
                name = input("Enter the new person's name: ").strip()
                open_space.add_person(name)
                print(f"✅ Added {name} and updated seating.")
            else:
                print("⚠️ No active OpenSpace instance. Re-run organisation first.")

        elif choice == "2":
            if open_space is not None:
                open_space.add_table()
                print("✅ Added a new table.")
            else:
                print("⚠️ No active OpenSpace instance. Re-run organisation first.")

        elif choice == "3":
            print("\n--- Add or Update Preference ---")
            person = input("Enter person's name: ").strip()
            sit_with = input("List people they want to sit WITH (comma-separated): ").strip()
            sit_without = input("List people they do NOT want to sit with (comma-separated): ").strip()

            preferences[person] = {
                "with": [p.strip() for p in sit_with.split(",") if p.strip()],
                "without": [p.strip() for p in sit_without.split(",") if p.strip()],
            }

            save_preferences_to_config(preferences)
            print(f"✅ Updated preferences for {person}. Re-running organisation...")

            if open_space is not None:
                current_people = [p for occupants in open_space.display().values() for p in occupants]
                open_space.organise(current_people, preferences=preferences, persistent=True)
            else:
                print("⚠️ No active OpenSpace instance to reorganise. Please run organisation first.")

        elif choice == "4":
            if open_space is not None:
                print("🔁 Reorganising everyone...")
                current_people = [p for occupants in open_space.display().values() for p in occupants]
                open_space.organise(current_people, preferences=preferences, persistent=True)
            else:
                print("⚠️ No active OpenSpace instance to reorganise.")

        elif choice == "r" and use_config == "y":
            print("\n🔁 Reloading configuration manually...")
            new_config = load_config()
            if new_config is not None:
                config = new_config
                open_space, preferences = run_organisation(config)
                if open_space:
                    last_modified = os.path.getmtime(CONFIG_PATH)
            else:
                print("⚠️ Failed to reload config.json.")

        elif choice == "5":
            print("👋 Exiting program. Goodbye!")
            break

        else:
            print("⚠️ Invalid option. Try again.")

        # --- Display updated seating ---
        if open_space is not None:
            seating = open_space.display()
            print("\nUpdated seating arrangement:")
            for table_name, occupants in seating.items():
                occupants_str = ", ".join(occupants) if occupants else "(empty)"
                print(f"  {table_name}: {occupants_str}")


if __name__ == "__main__":
    main()
