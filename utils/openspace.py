# UTF-8 Python 3.13.5
# Utility function for organising people into tables in an open space setting.
# Author: Intan K. Wardhani

import random, pandas as pd, table

class OpenSpace:
    
    """A class to organise people into tables in an open space setting.
    
    Attributes:
        tables (list): A list of Table objects representing the tables in the open space.
        number_of_tables (int): The total number of tables in the open space.
    Methods:
        organise(a_group: list) -> None:
            Organises a group of people into the available tables randomly.
    """
    
    def __init__(self, number_of_tables: int, capacity: int) -> None:
        self.tables = [table.Table(capacity) for _ in range(number_of_tables)]
        self.number_of_tables = number_of_tables
        
    def organise(self, a_group: list) -> None:
       
        self.a_whole_set = dict()
        
        for i in range(len(self.tables)):
            self._a_table = random.choice(self.tables)
            self.tables.remove(self._a_table)
            
            random.shuffle(a_group)
            self._a_group_part = a_group[:self._a_table.capacity]
            a_group = a_group[self._a_table.capacity:]
            
            # Initialize an empty list for this table
            table_key = f"Table {i+1}"
            self.a_whole_set[table_key] = []
            
            for self._person in self._a_group_part:
                print(f"Assigning {self._person} to Table {i + 1} with capacity {self._a_table.capacity}.")
                self._a_table.assign_seat(self._person)
                
                # Append each person to the table’s list
                self.a_whole_set[table_key].append(self._person)
        
    def display(self) -> dict:
        return self.a_whole_set

    def store(self, a_whole_set: dict, filename: str):
        data = [
            {'Table': table, 'Occupant': person}
            for table, occupants in self.a_whole_set.items()
            for person in occupants
        ]
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Data exported successfully to {filename}")
        
            
        
        
