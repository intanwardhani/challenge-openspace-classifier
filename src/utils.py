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
    def to_csv(snapshot, filename: str) -> None:
        """
        Export seating snapshot to CSV.

        Parameters
        ----------
        snapshot : SeatingSnapshot
            Normalised seating snapshot.
        filename : str
            Output filename. .csv will be appended if missing.
        """
        if not filename.lower().endswith(".csv"):
            filename += ".csv"

        rows = snapshot.rows()

        if not rows:
            raise ValueError("No seating data to export.")

        fieldnames = rows[0].keys()

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)


    @staticmethod
    def to_txt(snapshot, filename: str) -> None:
        """
        Export a verbose seating report to TXT.

        Parameters
        ----------
        snapshot : SeatingSnapshot
            Normalised snapshot of seating, preferences, and clusters.
        filename : str
            Output filename. .txt will be appended if missing.
        """
        
        if not filename.lower().endswith(".txt"):
            filename += ".txt"

        with open(filename, "w", encoding="utf-8") as f:
            # ---------- WITH preferences ----------
            f.write("WITH preferences:\n")
            if snapshot.with_prefs:
                for person, group in snapshot.with_prefs.items():
                    f.write(f"  {person}: {', '.join(group)}\n")
            else:
                f.write("  (none)\n")

            # ---------- WITHOUT preferences ----------
            f.write("\nWITHOUT preferences:\n")
            if snapshot.without_prefs:
                for person, group in snapshot.without_prefs.items():
                    f.write(f"  {person}: {', '.join(group)}\n")
            else:
                f.write("  (none)\n")

            # ---------- No-preference people ----------
            f.write("\nNo preferences:\n")
            if snapshot.no_preferences:
                f.write(f"  {', '.join(snapshot.no_preferences)}\n")
            else:
                f.write("  (none)\n")

            # ---------- Broken preferences ----------
            f.write("\nBroken preferences:\n")
            if snapshot.broken_preferences:
                for a, b in snapshot.broken_preferences:
                    f.write(f"  {a} cannot sit with {b}\n")
            else:
                f.write("  (none)\n")

            # ---------- Final clusters ----------
            f.write("\nFinal clusters:\n")
            if snapshot.clusters:
                for idx, cluster in enumerate(snapshot.clusters, start=1):
                    f.write(f"  Group {idx}: {', '.join(cluster)}\n")
            else:
                f.write("  (none)\n")

            # ---------- Seating assignments ----------
            f.write("\nSeating assignments:\n")
            for table_id, people in snapshot.by_table().items():
                seated = ", ".join(people) if people else "(empty)"
                f.write(f"  Table {table_id}: {seated}\n")


