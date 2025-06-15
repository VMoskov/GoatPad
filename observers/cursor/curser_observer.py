from abc import ABC, abstractmethod
from position.location import Location


class CursorObserver(ABC):
    @abstractmethod
    def update_cursor_location(self, location: Location):
        pass