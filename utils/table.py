# UTF-8 Python 3.13.5
# Utility functions for seat and table classes
# Author: Intan K. Wardhani

class Seat:
    
    """A class representing a seat in the openspace.
    
    Attributes:
        occupant (str): The name of the occupant of the seat.
        free (bool): Indicates whether the seat is free or occupied.
        
    Methods:
        set_occupant(name: str) -> None: Sets the occupant of the seat if it is free.
        remove_occupant() -> None: Removes the occupant of the seat if it is occupied.
    """
    
    def __init__(self) -> None:
        self.occupant = ""
        self.isfree = True

    def set_occupant(self, name: str) -> None:
        if self.isfree:
            self.occupant = name
            self.isfree = False
        else:
            print("Seat is already occupied")
        
    def remove_occupant(self) -> str:
        if not self.isfree:
            self.message = f"Removing occupant: {self.occupant}"
            self.__init__()
        return self.message
        
    
class Table:
    
    """A class representing a table with a certain capacity of seats.
    
    Attributes: 
        capacity (int): The maximum number of seats at the table.
        seats (list): A list of Seat objects representing the seats at the table.
        
    Methods:
        has_free_spot() -> bool: Checks if there is a free spot at the table.
        assign_seat(name: str) -> None: Assigns a seat to an occupant if there is a free spot.
        left_capacity() -> int: Returns the number of free spots left at the table.
    """
    
    def __init__(self, capacity: int, seats: list = []) -> None:
        self.capacity = capacity
        self.seats = seats
        
    def has_free_spot(self) -> bool:
        if len(self.seats) <= self.capacity:
            return True
        else:
            return False
        
    def assign_seat(self, name: str) -> None:
        while self.has_free_spot():
            self.__new_seat = Seat()
            self.__new_seat.set_occupant(name)
            self.seats.append(self.__new_seat)
            print(f"{name} has been assigned a seat.")
            break
            
    def left_capacity(self) -> int:
        return self.capacity - len(self.seats)

