# UTF-8 Python 3.13.5
# Utility function for organising people into tables in an open space setting.
# Author: Intan K. Wardhani

import random
from src.table import Table
from src.utils import FileManager

class OpenSpace:
    """
    A class to organise people into tables dynamically in an open space setting.
    Supports persistence and seating preferences.
    """

    def __init__(self, number_of_tables: int, capacity: int) -> None:
        self.tables = [Table(capacity) for _ in range(number_of_tables)]
        self.capacity_per_table = capacity
        self.a_whole_set = {}        # {table_name: [occupants]}
        self.previous_seating = {}   # persistent seating memory

    # ----------------------------------------------------
    # Core organisation logic
    # ----------------------------------------------------
    def organise(self, people: list[str], preferences: dict = None, persistent: bool = True) -> None:
        """
        Organise people randomly into tables with optional persistence and preferences.
        """

        # --- 1️⃣ Smart persistence: preserve existing seating ---
        if persistent and self.previous_seating:
            print("🧠 Applying smart persistence to keep existing seating...")
            people_to_seat = [p for p in people if p not in self._current_occupants()]
        else:
            people_to_seat = list(people)

        # --- 2️⃣ Handle over-allocation (too many people) ---
        total_capacity = len(self.tables) * self.capacity_per_table
        while len(people_to_seat) > total_capacity:
            self.add_table()
            total_capacity = len(self.tables) * self.capacity_per_table

        # --- 3️⃣ Apply seating preferences if provided ---
        if preferences:
            people_to_seat = self._apply_preferences(people_to_seat, preferences)

        # --- 4️⃣ Assign people dynamically ---
        random.shuffle(people_to_seat)
        for person in people_to_seat:
            assigned = False
            for table in self.tables:
                if table.has_free_spot() and not self._violates_preferences(table, person, preferences):
                    table.assign_seat(person)
                    assigned = True
                    break
            if not assigned:
                # Add a new table dynamically if needed
                self.add_table()
                self.tables[-1].assign_seat(person)

        # --- 5️⃣ Update and store persistent state ---
        self._refresh_seating()
        self.previous_seating = self.a_whole_set.copy()

    # ----------------------------------------------------
    # Preference handling
    # ----------------------------------------------------
    def _apply_preferences(self, people: list[str], preferences: dict) -> list[str]:
        """Group people who want to sit together."""
        grouped = []
        visited = set()
        for person in people:
            if person in visited:
                continue
            group = [person]
            with_list = preferences.get(person, {}).get("with", [])
            for partner in with_list:
                if partner in people:
                    group.append(partner)
                    visited.add(partner)
            visited.add(person)
            grouped.append(group)
        # Flatten grouped people but keep their adjacency in order
        return [p for group in grouped for p in group]

    def _violates_preferences(self, table: Table, person: str, preferences: dict) -> bool:
        """Return True if seating the person here breaks 'without' preferences."""
        if not preferences or person not in preferences:
            return False
        avoid_list = set(preferences[person].get("without", []))
        current = set(table.occupants())
        return not avoid_list.isdisjoint(current)

    # ----------------------------------------------------
    # Dynamic updates
    # ----------------------------------------------------
    def add_person(self, name: str) -> None:
        """Add a new person dynamically, preserving seating."""
        for table in self.tables:
            if table.has_free_spot():
                table.assign_seat(name)
                self._refresh_seating()
                print(f"{name} added to an existing table.")
                self.previous_seating = self.a_whole_set.copy()
                return
        print("No free table — adding a new one.")
        self.add_table()
        self.tables[-1].assign_seat(name)
        self._refresh_seating()
        self.previous_seating = self.a_whole_set.copy()

    def add_table(self) -> None:
        """Add a new table dynamically."""
        new_table = Table(self.capacity_per_table)
        self.tables.append(new_table)
        print(f"New table added. Total tables: {len(self.tables)}")

    # ----------------------------------------------------
    # Helper utilities
    # ----------------------------------------------------
    def _current_occupants(self) -> list[str]:
        """Return a flat list of all current occupants."""
        return [p for occupants in self.previous_seating.values() for p in occupants]

    def _refresh_seating(self) -> None:
        """Rebuild internal seating dictionary."""
        self.a_whole_set.clear()
        for i, table in enumerate(self.tables, start=1):
            self.a_whole_set[f"Table {i}"] = table.occupants()

    def display(self) -> dict:
        """Return current seating arrangement."""
        return self.a_whole_set

    def store(self, filename: str, export: bool = True):
        """Export seating arrangement to CSV if export=True."""
        if export:
            FileManager.export_csv(self.a_whole_set, filename)


