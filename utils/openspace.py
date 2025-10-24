# UTF-8 Python 3.13.5
# Utility function for organising people into tables in an open space setting.
# Author: Intan K. Wardhani

import random, table

class OpenSpace:
    
    def __init__(self, number_of_tables: int, capacity: int) -> None:
        self.tables = [table.Table(capacity) for _ in range(number_of_tables)]
        self.number_of_tables = number_of_tables
        
    def organise(self, a_group: list = []) -> None:
        # self._a_table = random.choice(self.tables)
        # self._table_capacity = self._a_table.capacity
        # self._a_group = random.shuffle(names)
        # for name in names:
        #     while not self._a_table.has_free_spot():
        #         self._a_table = random.choice(self.tables)
        #     self._a_table.assign_seat(name)
        
        # for i, self._a_table in enumerate(self.tables):
        #     random.shuffle(a_group)
        #     self._a_group_part = a_group[:self._a_table.left_capacity()]
        #     a_group = a_group[self._a_table.left_capacity():]
        #     if self._a_table.has_free_spot():
        #         for self._person in self._a_group_part:
        #             self._a_table.assign_seat(self._person)
        #         print(f"Table {i} has {self._a_table.capacity} seats occupied.")
        #         print(f"There are {self._a_table.left_capacity()} seat(s) left at Table {i+1}.")
        #     else:
        #         print(f"Sorry, no free spots available at Table {i+1}.")
        
        self._a_table = random.choice(self.tables)
        self.tables.remove(self._a_table)
        
        random.shuffle(a_group)
        self._a_group_part = a_group[:self._a_table.capacity]
        self._a_group = a_group[self._a_table.capacity:]
        for self._person in self._a_group_part:
            self._a_table.assign_seat(self._person)
        
            
        
        
