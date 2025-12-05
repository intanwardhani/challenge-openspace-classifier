# UTF-8 Python 3.13.5
# Utility functions for file managers
# Author: Intan K. Wardhani

import pandas as pd

class FileManager:
    """
    A utility class for importing and exporting CSV files.

    Methods:
        import_csv(filename: str) -> list[str]:
            Reads a one-column CSV file containing names and returns them as a list.
        export_csv(data: dict, filename: str) -> None:
            Exports a dictionary of table assignments to a CSV file.
    """

    @staticmethod
    def import_csv(filename: str) -> list[str]:
        """
        Import a CSV file containing a single column of names.

        Args:
            filename (str): Path to the CSV file.

        Returns:
            list[str]: A list of names.
        """
        
        df = pd.read_csv(filename, header=None)
        return df[0].tolist()

    @staticmethod
    def export_csv(data: dict, filename: str) -> None:
        """
        Export table assignments to a CSV file.

        Args:
            data (dict): A dictionary where keys are table names and values are lists of occupants.
            filename (str): Path to save the CSV file.
        """
        
        records = [{'Table': table, 'Occupant': occupant} for table, occupants in data.items() for occupant in occupants]
        df = pd.DataFrame(records)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Data successfully exported to {filename}")