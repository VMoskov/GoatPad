from dataclasses import dataclass, field
from .location import Location

@dataclass
class LocationRange:
    start: Location
    end: Location

    def __post_init__(self):
        # make sure that start is always before end
        if self.start.row > self.end.row or \
           (self.start.row == self.end.row and self.start.column > self.end.column):
            self.start, self.end = self.end, self.start
            
    def is_empty(self):
        return self.start == self.end