# UTF-8 Python 3.13.5
# Utility functions for seat and table classes
# Author: Intan K. Wardhani

class Seat:
    """Represents a seat with an occupant and free/occupied status."""

    def __init__(self) -> None:
        self.occupant = ""
        self.isfree = True

    def set_occupant(self, name: str) -> None:
        if self.isfree:
            self.occupant = name
            self.isfree = False
        else:
            print(f"Seat is already occupied by {self.occupant}.")

    def remove_occupant(self) -> str:
        if not self.isfree:
            message = f"Removing occupant: {self.occupant}"
            self.__init__()  # reset
            return message
        return "Seat is already free."

    def __str__(self) -> str:
        return f"Occupant: {self.occupant}, Free: {self.isfree}"


class Table:
    """A table that can hold multiple seats."""

    def __init__(self, capacity: int, seats: list = None) -> None:
        self.capacity = capacity
        self.seats = seats if seats is not None else []

    def has_free_spot(self) -> bool:
        return len(self.seats) < self.capacity

    def assign_seat(self, name: str) -> bool:
        """Try to assign a person to a free seat. Return True if successful."""
        if self.has_free_spot():
            new_seat = Seat()
            new_seat.set_occupant(name)
            self.seats.append(new_seat)
            print(f"{name} has been assigned to a seat at a table.")
            return True
        return False

    def left_capacity(self) -> int:
        return self.capacity - len(self.seats)

    def occupants(self) -> list:
        return [seat.occupant for seat in self.seats]
    
    def seat_names(self) -> list[str]:
        """Return a list of names of people seated at this table."""
        return [seat.occupant for seat in self.seats]

    def __str__(self) -> str:
        occupants = [seat.occupant for seat in self.seats]
        return f"Table (capacity: {self.capacity}, occupants: {occupants})"