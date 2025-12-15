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
            occupants.update(table.assigned.values())
        return occupants

    def _refresh_seating(self):
        """
        Refresh `self.a_whole_set` and `self.previous_seating`
        based on the current seating across all tables.
        """
        self.a_whole_set = []
        self.previous_seating = {}

        for table in self.tables:
            assigned_list = [p for p in table.assigned.values() if p]
            self.a_whole_set.append((table.name, assigned_list))

            for seat_index, person in table.assigned.items():
                if person:
                    self.previous_seating[person] = (table.name, seat_index)

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
            if table.name == name:
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
        for seated_person in table.assigned.values():
            if seated_person and seated_person in forbidden:
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
            if all(table.assigned.values()):
                continue

            # Check WITHOUT constraints
            if self._violates_without_preferences(person, table, preferences):
                continue

            # If restricting to free people, ensure the table has only free individuals
            if free_people_only:
                all_free = True
                for p in table.assigned.values():
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
            for seat_idx, person in table.assigned.items():
                if not person:
                    continue
                # Free = no WITH/WITHOUT OR singleton cluster
                if person not in with_prefs and person not in without_prefs:
                    free_individuals.append(person)
                else:
                    clustered.add(person)

        # Compute average target table size
        total_people = len([p for table in self.tables for p in table.assigned.values() if p])
        num_tables = len(self.tables)
        target_size = total_people // num_tables
        extra = total_people % num_tables  # tables allowed to have +1

        # Build table -> assigned free people mapping
        table_free_map = defaultdict(list)
        for table in self.tables:
            for seat_idx, person in table.assigned.items():
                if person in free_individuals:
                    table_free_map[table.name].append(person)

        # Attempt redistribution
        for table in self.tables:
            current = len([p for p in table.assigned.values() if p])
            allowed = target_size + (1 if extra > 0 else 0)
            if current > allowed:
                # Move excess free people
                excess = current - allowed
                movable = [p for p in table.assigned.values() if p in free_individuals]
                for p in movable[:excess]:
                    dest_table = self._find_table_for_person(p, preferences, free_people_only=True)
                    if dest_table and dest_table.name != table.name:
                        # Swap/move
                        # Remove from current table
                        for seat_idx, sp in table.assigned.items():
                            if sp == p:
                                table.assigned[seat_idx] = None
                                break
                        # Assign to new table
                        for seat_idx, sp in dest_table.assigned.items():
                            if sp is None:
                                dest_table.assigned[seat_idx] = p
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
                from table import Table
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
                from table import Table
                new_table = Table(new_table_name, capacity)
                new_table.assign_seat(person)
                self.tables.append(new_table)

        # ------ Step 7: Soft balancing pass ------
        self._soft_balance_tables(preferences)

        # ------ Step 8: Refresh internal seating states ------
        self._refresh_seating()
    
    # -------------------------
    # Additional helpers
    # -------------------------

    def print_current_seating(self):
        """
        Print current seating for logging / debugging.
        """
        for table in self.tables:
            seated = [p for p in table.assigned.values() if p]
            print(f"{table.name}: {', '.join(seated)}")

    # End of class OpenSpace







