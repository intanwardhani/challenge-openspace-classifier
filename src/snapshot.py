# UTF-8 Python 3.13.5
# Data adaptor/interpreter between OpenSpace and FileManager
# Author: Intan K. Wardhani

from typing import Dict, List, Any

class SeatingSnapshot:
    """
    Read-only, normalised view of an OpenSpace instance.
    Produces one row per person, suitable for CSV and TXT export.
    """
    
    def __init__(self, open_space, preferences: Dict[str, Dict[str, List[str]]]):
        self.open_space = open_space
        self.preferences = preferences
        
    
    # -------------------------
    # Public API
    # -------------------------
    
    def rows(self) -> List[Dict[str, Any]]:
        """
        Return canonical seating rows.

        Columns:
        - Name
        - Table (numeric ID)
        - WithPref
        - WithoutPref
        - Cluster
        """
        
        rows: List[Dict[str, Any]] = []

        # build cluster lookup
        cluster_map = self._build_cluster_map()

        # iterate tables in numeric order
        for table in self._tables_sorted():
            table_id = self._table_id(table)

            for seat in table.seats:
                if not seat.occupant:
                    continue

                name = seat.occupant
                rows.append({
                    "Name": name,
                    "Table": table_id,
                    "WithPref": ", ".join(self.preferences.get("with", {}).get(name, [])),
                    "WithoutPref": ", ".join(self.preferences.get("without", {}).get(name, [])),
                    "Cluster": cluster_map.get(name, ""),
                })

        return rows


    # -------------------------
    # Internal helpers
    # -------------------------

    def _tables_sorted(self):
        """Return tables sorted by numeric table id."""
        return sorted(
            self.open_space.tables,
            key=lambda t: self._table_id(t)
        )
        
    @staticmethod
    def _table_id(table) -> int:
        """Extract numeric ID from table.table_name."""
        try:
            return int(table.table_name.split()[-1])
        except (ValueError, IndexError):
            raise ValueError(f"Invalid table name format: {table.table_name}")
        
    def _build_cluster_map(self) -> Dict[str, int]:
        """
        Build person → cluster_id mapping.
        """
        cluster_map: Dict[str, int] = {}

        if not hasattr(self.open_space, "clusters"):
            return cluster_map

        for idx, cluster in enumerate(self.open_space.clusters, start=1):
            for person in cluster:
                cluster_map[person] = idx

        return cluster_map