# UTF-8 Python 3.13.5
# Author: Intan K. Wardhani

import random
from collections import defaultdict, deque

"""
OpenSpace
---------

This class organises people into tables following several rules:
- WITH preferences form two-way clusters (connected components)
- WITHOUT preferences override WITH and may split clusters
- Clusters are seated first before single individuals
- The system avoids lonely tables when possible
- A soft balancing pass redistributes free individuals so table sizes differ by ≤ 1
- Existing seating is preserved when `persistent=True` to minimise movement
- No output is written here; main.py handles exporting seating.txt
"""

class OpenSpace:
    def __init__(self, people, tables, config):
        """
        Initialise the OpenSpace seating system.

        Parameters
        ----------
        people : list[str]
            List of all participant names.
        tables : list[Table]
            List of table objects (from table.py) with capacity and assigned seats.
        config : dict
            Configuration values loaded from config.json.
        """
        self.people = people
        self.tables = tables
        self.config = config

        # seating states
        self.previous_seating = {}   # for persistent mode
        self.a_whole_set = []        # list of (table_name, [people])
    
    # -------------------------
    # Seating / state utilities
    # -------------------------

    def _current_occupants(self):
        """
        Return a set of all people currently seated across all tables.
        """
        occupants = set()
        for table in self.tables:
            occupants.update(seat.occupant for seat in table.seats if seat.occupant)
        return occupants

    def _refresh_seating(self):
        """
        Refresh `self.a_whole_set` and `self.previous_seating`
        based on the current seating across all tables.
        """
        self.a_whole_set = []
        self.previous_seating = {}

        for table in self.tables:
            assigned_list = [seat.occupant for seat in table.seats if seat.occupant]
            self.a_whole_set.append((table.table_name, assigned_list))

            for seat_index, seat in enumerate(table.seats):
                if seat.occupant:
                    self.previous_seating[seat.occupant] = (table.table_name, seat_index)

    def _reset_tables(self):
        """
        Clear all assigned seats across all tables.
        """
        for table in self.tables:
            table.clear_assignments()

    def _lookup_table_by_name(self, name):
        """
        Return the table object matching the given name.
        """
        for table in self.tables:
            if table.table_name == name:
                return table
        return None

    def _violates_without_preferences(self, person, table, preferences):
        """
        Check whether seating `person` at this `table` violates WITHOUT preferences.
        Returns True if any co-seated person is forbidden.

        Note: This is used only for individual seating after clusters are placed.
        """
        without_map = preferences.get("without", {})
        forbidden = set(without_map.get(person, []))

        # anyone already at this table?
        for seat in table.seats:
            if seat.occupant and seat.occupant in forbidden:
                return True

        return False
    
    # -------------------------
    # Preference graph helpers
    # -------------------------

    def _build_with_graph(self, preferences):
        """
        Build an undirected graph from the 'with' preferences.
        Returns: dict[person] -> set of connected people
        """
        graph = defaultdict(set)
        with_prefs = preferences.get("with", {})

        for person, with_list in with_prefs.items():
            for other in with_list:
                graph[person].add(other)
                graph[other].add(person)  # two-way link

        return graph

    def _apply_without_constraints(self, graph, preferences):
        """
        Remove edges in the WITH graph that violate any WITHOUT constraints.
        Returns a list of removed edges (tuples).
        """
        without_prefs = preferences.get("without", {})
        removed_edges = []

        for person, blocked_list in without_prefs.items():
            for forbidden in blocked_list:
                if forbidden in graph[person]:
                    graph[person].remove(forbidden)
                    graph[forbidden].remove(person)
                    removed_edges.append((person, forbidden))

        return removed_edges

    def _get_connected_components(self, graph, all_people):
        """
        Compute connected components after splitting forbidden edges.
        Returns a list of lists (each inner list is a cluster).
        """
        visited = set()
        components = []

        for person in all_people:
            if person not in visited:
                queue = deque([person])
                visited.add(person)
                component = [person]

                while queue:
                    node = queue.popleft()
                    for neighbor in graph[node]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                            component.append(neighbor)

                components.append(component)

        return components

    def _print_broken_groups(self, removed_edges, components, preferences_label="[preferences]"):
        """
        Print messages for broken WITH clusters due to WITHOUT rules.
        """
        if not removed_edges:
            return

        print(f"{preferences_label} Some seating preferences were split due to 'without' rules:")

        for a, b in removed_edges:
            print(f"{preferences_label} {a} cannot be seated with {b}.")

        # Summary of new groupings
        print(f"{preferences_label} Resulting groups:")
        for comp in components:
            if len(comp) > 1:
                print(f"{preferences_label}  • {', '.join(comp)}")
                
    # -------------------------
    # Swap / balance helpers
    # -------------------------

    def _find_table_for_person(self, person, preferences, free_people_only=False):
        """
        Find a suitable table for `person` without violating WITHOUT preferences.
        If free_people_only=True, only tables with free individuals are considered for balancing.
        Returns: table object or None if no valid table found.
        """
        for table in self.tables:
            # Skip table if full
            if all(seat.occupant for seat in table.seats):
                continue

            # Check WITHOUT constraints
            if self._violates_without_preferences(person, table, preferences):
                continue

            # If restricting to free people, ensure the table has only free individuals
            if free_people_only:
                all_free = True
                for seat in table.seats:
                    p = seat.occupant
                    if p and (p in preferences.get("with", {}) or p in preferences.get("without", {})):
                        all_free = False
                        break
                if not all_free:
                    continue

            return table

        return None

    def _soft_balance_tables(self, preferences):
        """
        Softly balance table sizes so they differ by at most 1.
        Moves only free individuals (singleton clusters or no preferences).
        """
        # Identify free individuals
        clustered = set()
        with_prefs = preferences.get("with", {})
        without_prefs = preferences.get("without", {})

        free_individuals = []
        for table in self.tables:
            for _, seat in enumerate(table.seats):
                person = seat.occupant
                if not person:
                    continue
                # Free = no WITH/WITHOUT OR singleton cluster
                if person not in with_prefs and person not in without_prefs:
                    free_individuals.append(person)
                else:
                    clustered.add(person)

        # Compute average target table size
        total_people = len([seat.occupant for table in self.tables for seat in table.seats if seat.occupant])
        num_tables = len(self.tables)
        target_size = total_people // num_tables
        extra = total_people % num_tables  # tables allowed to have +1

        # Build table -> assigned free people mapping
        table_free_map = defaultdict(list)
        for table in self.tables:
            for seat_idx, seat in enumerate(table.seats):
                person = seat.occupant
                if person in free_individuals:
                    table_free_map[table.table_name].append(person)

        # Attempt redistribution
        for table in self.tables:
            current = len([seat.occupant for seat in table.seats if seat.occupant])
            allowed = target_size + (1 if extra > 0 else 0)
            if current > allowed:
                # Move excess free people
                excess = current - allowed
                movable = [seat.occupant for seat in table.seats if seat.occupant in free_individuals]
                for p in movable[:excess]:
                    dest_table = self._find_table_for_person(p, preferences, free_people_only=True)
                    if dest_table and dest_table.name != table.name:
                        # Swap/move
                        # Remove from current table
                        for seat in table.seats:
                            if seat.occupant == p:
                                seat.occupant = ""
                                seat.isfree = True
                                break
                        # Assign to new table
                        for seat in dest_table.seats:
                            if seat.isfree:
                                seat.occupant = p
                                seat.isfree = False
                                break
                if extra > 0:
                    extra -= 1

    def organise(self, preferences, persistent=False):
        """
        Main seating organiser.

        Parameters
        ----------
        preferences : dict
            Dictionary containing "with" and "without" preferences.
        persistent : bool
            If True, preserve previous seating for minimal movement.
        """
        
        # ------ Step 0: Reset tables if not persistent ------
        if not persistent:
            self._reset_tables()

        # ------ Step 1: Build two-way WITH graph ------
        with_graph = self._build_with_graph(preferences)

        # ------ Step 2: Remove edges violating WITHOUT ------
        removed_edges = self._apply_without_constraints(with_graph, preferences)

        # ------ Step 3: Get clusters (connected components) ------
        clusters = self._get_connected_components(with_graph, self.people)

        # ------Step 4: Log broken clusters ------
        self._print_broken_groups(removed_edges, clusters, preferences_label="[preferences]")

        # ------ Step 5: Seat clusters first ------
        clusters_sorted = sorted(clusters, key=lambda c: -len(c))  # largest first
        for cluster in clusters_sorted:
            assigned = False
            for table in self.tables:
                if table.left_capacity() >= len(cluster):
                    for person in cluster:
                        table.assign_seat(person)
                    assigned = True
                    break
            if not assigned:
                # No table can fit cluster → add new table
                new_table_name = f"Table {len(self.tables)+1}"
                capacity = self.config.get("table_capacity", 5)
                from src.table import Table
                new_table = Table(new_table_name, capacity)
                for person in cluster:
                    new_table.assign_seat(person)
                self.tables.append(new_table)

        # ------ Step 6: Seat remaining single individuals ------
        seated_people = set(p for table in self.tables for p in table.occupants())
        remaining_people = [p for p in self.people if p not in seated_people]

        random.shuffle(remaining_people)  # random placement for fairness

        for person in remaining_people:
            table = self._find_table_for_person(person, preferences)
            if table:
                table.assign_seat(person)
            else:
                # Must add new table
                new_table_name = f"Table {len(self.tables)+1}"
                capacity = self.config.get("table_capacity", 5)
                from src.table import Table
                new_table = Table(new_table_name, capacity)
                new_table.assign_seat(person)
                self.tables.append(new_table)

        # ------ Step 7: Soft balancing pass ------
        self._soft_balance_tables(preferences)

        # ------ Step 8: Refresh internal seating states ------
        self._refresh_seating()
        
        # ------ Step 9: Enable local variables for FileManager ------
        self.removed_edges = removed_edges
        self.clusters = clusters
    
    # -------------------------
    # Additional helpers
    # -------------------------

    def print_current_seating(self):
        """
        Print current seating for logging / debugging.
        """
        for table in self.tables:
            seated = [seat.occupant for seat in table.seats if seat.occupant]
            print(f"{table.table_name}: {', '.join(seated)}")
            
    def display(self) -> dict[str, list[str]]:
        """
        Print a compact, symmetric visual illustration of seating.
        Visualisation is decorative and does not imply semantic seat geometry.

        Returns:
            dict[str, list[str]]: {table_name: [occupants]}
        """
        table_map = {}

        for table in self.tables:
            occupants = [seat.occupant for seat in table.seats]
            capacity = len(occupants)
            real_people = [p for p in occupants if p]

            table_map[table.table_name] = real_people.copy()

            # ---------- visual slot containers ----------
            top_row: list[str] = []
            bottom_row: list[str] = []
            left_side: str = ""
            right_side: str = ""

            # ---------- placement order ----------
            slots = []

            # top row (grows left → right)
            slots.append(("top",))
            slots.append(("top",))

            # bottom row (grows left → right)
            slots.append(("bottom",))
            slots.append(("bottom",))

            # sides
            slots.append(("left",))
            slots.append(("right",))

            # expand rows symmetrically if needed
            while len(slots) < capacity:
                slots.append(("top",))
                slots.append(("bottom",))
                slots.append(("left",))
                slots.append(("right",))

            # ---------- assign occupants to visual slots ----------
            padded_people = occupants + [""] * (capacity - len(occupants))

            for person, slot in zip(padded_people, slots):
                target = slot[0]
                if target == "top":
                    top_row.append(person or "")
                elif target == "bottom":
                    bottom_row.append(person or "")
                elif target == "left" and not left_side:
                    left_side = person or ""
                elif target == "right" and not right_side:
                    right_side = person or ""

            # ---------- formatting ----------
            all_names = [p for p in occupants if p]
            max_name_len = max((len(p) for p in all_names), default=1)
            seat_width = max(max_name_len, 3)

            def fmt(name: str) -> str:
                return f"({name.center(seat_width)})"

            top_str = " ".join(fmt(p) for p in top_row)
            bottom_str = " ".join(fmt(p) for p in bottom_row)

            left_str = fmt(left_side) if left_side else fmt("")
            right_str = fmt(right_side) if right_side else fmt("")

            table_label = f" {table.table_name} "
            table_width = max(
                len(top_str),
                len(bottom_str),
                len(table_label),
            )

            border = "-" * table_width
            table_line = table_label.center(table_width)

            # ---------- render ----------
            print()
            if top_row:
                print(top_str.center(table_width))
            print(f"{left_str} {border} {right_str}")
            print(f"{left_str} {table_line} {right_str}")
            print(f"{left_str} {border} {right_str}")
            if bottom_row:
                print(bottom_str.center(table_width))

        return table_map




    # End of class OpenSpace