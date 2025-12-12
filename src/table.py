# UTF-8 Python 3.13.5
# Table and Seat classes for Openspace Organisr
# Author: Intan K. Wardhani

class Seat:
    """Represents a single seat in a table."""
    def __init__(self):
        self.occupant = ""
        self.isfree = True


class Table:
    """Represents a table with multiple seats."""

    def __init__(self, table_name: str, capacity: int, seats: list[Seat] | None = None):
        """
        Initialize a table.

        Args:
            table_name (str): Human-readable name for the table, e.g., "Table 1".
            capacity (int): Maximum number of seats at the table.
            seats (list[Seat], optional): Existing seats to initialize the table. Defaults to None.
        """
        self.table_name = table_name
        self.capacity = capacity
        self.seats = seats if seats is not None else [Seat() for _ in range(capacity)]

    def has_free_spot(self) -> bool:
        """Check if there is at least one free seat."""
        return any(seat.isfree for seat in self.seats)

    def assign_seat(self, name: str) -> bool:
        """
        Assign a person to the first available free seat.

        Args:
            name (str): Name of the person to assign.

        Returns:
            bool: True if assignment succeeded, False if table is full.
        """
        for seat in self.seats:
            if seat.isfree:
                seat.occupant = name
                seat.isfree = False
                return True
        return False

    def left_capacity(self) -> int:
        """Return the number of free seats remaining."""
        return sum(1 for seat in self.seats if seat.isfree)

    def occupants(self) -> list[str]:
        """Return a list of names of people currently seated."""
        return [seat.occupant for seat in self.seats if seat.occupant is not None]

    def seat_names(self) -> list[str]:
        """Return a list of occupant names, None if empty."""
        return [seat.occupant for seat in self.seats]

    def clear_assignments(self):
        """Clear all assigned seats for reorganisation."""
        for seat in self.seats:
            seat.occupant = ""
            seat.isfree = True
