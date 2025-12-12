# UTF-8 Python 3.13.5
# Utility functions for Openspace Organisr
# Author: Intan K. Wardhani

import csv
from typing import List, Dict, Any

class FileManager:
    """Class to handle CSV and TXT import/export operations."""

    @staticmethod
    def from_csv(filename: str) -> List[Dict[str, Any]]:
        """
        Load data from a CSV file and return as list of dictionaries.

        Parameters
        ----------
        filename : str
            Path to the CSV file.

        Returns
        -------
        List[Dict[str, Any]]
            List of row dictionaries from CSV.
        """
        data = []
        with open(filename, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
        return data

    @staticmethod
    def to_csv(data: List[Dict[str, Any]], filename: str) -> None:
        """
        Export data to CSV.

        Parameters
        ----------
        data : List[Dict[str, Any]]
            List of row dictionaries to export.
        filename : str
            Output filename. .csv will be appended if missing.
        """
        if not filename.lower().endswith(".csv"):
            filename += ".csv"

        if not data:
            raise ValueError("No data to export.")

        fieldnames = data[0].keys()
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

    @staticmethod
    def to_txt(open_space, preferences: Dict[str, Dict[str, List[str]]], filename: str) -> None:
        """
        Export the current seating and historical logs to a TXT file.

        Includes:
        - WITH groups
        - WITHOUT constraints
        - No preference people
        - Broken preferences
        - Final clusters
        - Seating assignments

        Parameters
        ----------
        open_space : OpenSpace
            The OpenSpace instance containing tables and seating info.
        preferences : dict
            The preferences dict with "with" and "without" info.
        filename : str
            Output filename. .txt will be appended if missing.
        """
        if not filename.lower().endswith(".txt"):
            filename += ".txt"

        with open(filename, "w", encoding="utf-8") as f:
            # WITH groups
            f.write("WITH groups:\n")
            with_prefs = preferences.get("with", {})
            if with_prefs:
                for person, group in with_prefs.items():
                    f.write(f"  {person}: {', '.join(group)}\n")
            else:
                f.write("  (none)\n")

            # WITHOUT constraints
            f.write("WITHOUT constraints:\n")
            without_prefs = preferences.get("without", {})
            if without_prefs:
                for person, group in without_prefs.items():
                    f.write(f"  {person}: {', '.join(group)}\n")
            else:
                f.write("  (none)\n")

            # No-preference people
            no_prefs = [p for p in open_space.people if p not in with_prefs and p not in without_prefs]
            f.write("No preferences:\n")
            if no_prefs:
                f.write(f"  {', '.join(no_prefs)}\n")
            else:
                f.write("  (none)\n")

            # Broken preferences / removed edges
            f.write("Broken preferences:\n")
            if hasattr(open_space, "removed_edges") and open_space.removed_edges:
                for a, b in open_space.removed_edges:
                    f.write(f"  {a} cannot sit with {b}\n")
            else:
                f.write("  (none)\n")

            # Final clusters
            f.write("Final clusters:\n")
            if hasattr(open_space, "clusters") and open_space.clusters:
                for idx, cluster in enumerate(open_space.clusters, start=1):
                    f.write(f"  Group {idx}: {', '.join(cluster)}\n")
            else:
                f.write("  (none)\n")

            # Seating assignments
            f.write("Seating assignments:\n")
            for table in open_space.tables:
                seated = [p for p in table.assigned.values() if p]
                seated_str = ", ".join(seated) if seated else "(empty)"
                f.write(f"  {table.name}: {seated_str}\n")
