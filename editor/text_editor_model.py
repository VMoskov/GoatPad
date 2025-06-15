from position.location_range import LocationRange
from position.location import Location
from observers.cursor.curser_observer import CursorObserver
from observers.text.text_observer import TextObserver
from commands.insert_text_action import InsertTextAction
from commands.delete_action import DeleteAction
from stack.undo_manager import UndoManager


class TextEditorModel:
    def __init__(self, text=''):
        self.lines = text.split('\n') if text else []
        self.cursor_location = Location(0, 0)
        self.selection_range = LocationRange(start=Location(0, 0), end=Location(0, 0))
        self.cursor_observers = []
        self.text_observers = []

        self.undo_manager = UndoManager.get_instance()

    def all_lines(self):
        for line in self.lines:
            yield line

    def lines_range(self, index1, index2):
        if index1 < 0 or index2 >= len(self.lines):
            raise IndexError('Index out of range')
        for i in range(index1, index2):
            yield self.lines[i]

    # --- Cursor movement methods ---
    def do_move_left(self):
        if self.cursor_location.column > 0:
            self.cursor_location.column -= 1
        elif self.cursor_location.row > 0:
            self.cursor_location.row -= 1
            self.cursor_location.column = len(self.lines[self.cursor_location.row])
        self.notify_cursor_observers()

    def move_cursor_left(self):
        self.set_selection_range(start=self.cursor_location, end=self.cursor_location)
        self.do_move_left()

    def do_move_right(self):
        if self.cursor_location.column < len(self.lines[self.cursor_location.row]):
            self.cursor_location.column += 1
        elif self.cursor_location.row < len(self.lines) - 1:
            self.cursor_location.row += 1
            self.cursor_location.column = 0
        self.notify_cursor_observers()

    def move_cursor_right(self):
        self.set_selection_range(start=self.cursor_location, end=self.cursor_location)
        self.do_move_right()

    def do_move_up(self):
        if self.cursor_location.row > 0:
            self.cursor_location.row -= 1
            self.cursor_location.column = min(self.cursor_location.column, len(self.lines[self.cursor_location.row]))
        # if in the first line, go to the start of the line
        elif self.cursor_location.row == 0:
            self.cursor_to_document_start()
        self.notify_cursor_observers()

    def move_cursor_up(self):
        self.set_selection_range(start=self.cursor_location, end=self.cursor_location)
        self.do_move_up()

    def do_move_down(self):
        if self.cursor_location.row < len(self.lines) - 1:
            self.cursor_location.row += 1
            self.cursor_location.column = min(self.cursor_location.column, len(self.lines[self.cursor_location.row]))
        # if in the last line, go to the end of the line
        elif self.cursor_location.row == len(self.lines) - 1:
            self.cursor_to_document_end()
        self.notify_cursor_observers()

    def move_cursor_down(self):
        self.set_selection_range(start=self.cursor_location, end=self.cursor_location)
        self.do_move_down()

    # --- Observer methods ---
    def add_cursor_observer(self, observer: CursorObserver):
        self.cursor_observers.append(observer)

    def remove_cursor_observer(self, observer: CursorObserver):
        self.cursor_observers.remove(observer)

    def add_text_observer(self, observer: TextObserver):
        self.text_observers.append(observer)

    def remove_text_observer(self, observer: TextObserver):
        self.text_observers.remove(observer)

    def notify_cursor_observers(self):
        for observer in self.cursor_observers:
            observer.update_cursor_location(self.cursor_location)
    
    def notify_text_observers(self):
        for observer in self.text_observers:
            observer.update_text()

    # --- Cursor and selection methods ---
    def get_cursor_location(self):
        return self.cursor_location
    
    def set_cursor_location(self, location: Location):
        if (0 <= location.row < len(self.lines) and
                0 <= location.column <= len(self.lines[location.row])):
            self.cursor_location = location
            self.notify_cursor_observers()
        else:
            raise IndexError('Cursor location out of bounds')
        
    def get_selection_range(self):
        return self.selection_range
    
    def set_selection_range(self, start: Location, end: Location):
        self.selection_range = LocationRange(start, end)
        self.notify_text_observers()

    def get_text_from_range(self, loc_range: LocationRange):
        if loc_range.is_empty():
            return ''
        
        start_row, start_col = loc_range.start.row, loc_range.start.column
        end_row, end_col = loc_range.end.row, loc_range.end.column
        
        if start_row == end_row:  # range within a single line
            return self.lines[start_row][start_col:end_col]
        
        text_parts = []
        text_parts.append(self.lines[start_row][start_col:])  # part of the first line
        for row in range(start_row + 1, end_row):  # full lines in between
            text_parts.append(self.lines[row])
        text_parts.append(self.lines[end_row][:end_col])  # part of the last line
        
        return '\n'.join(text_parts)
    
    def select_all(self):
        if not self.lines:
            return
        
        start = Location(0, 0)
        end = Location(len(self.lines) - 1, len(self.lines[-1]))
        self.set_selection_range(start, end)
        self.set_cursor_location(end)

    def cursor_to_document_start(self):
        start_location = Location(0, 0)
        self.set_cursor_location(start_location)
        self.set_selection_range(start_location, start_location)

    def cursor_to_document_end(self):
        if not self.lines:
            return
        
        end_location = Location(len(self.lines) - 1, len(self.lines[-1]))
        self.set_cursor_location(end_location)
        self.set_selection_range(end_location, end_location)

    # --- Text manipulation methods ---
    def get_text(self):
        return '\n'.join(self.lines)
    
    def set_text(self, text):
        self.lines = text.split('\n')
        self.cursor_location = Location(0, 0)
        self.selection_range = LocationRange(start=Location(0, 0), end=Location(0, 0))

        self.notify_text_observers()
        self.notify_cursor_observers()

    def insert(self, text):
        if not self.selection_range.is_empty():
            delete_cmd = DeleteAction(self, self.selection_range)
            self.undo_manager.push(delete_cmd)
        
        insert_cmd = InsertTextAction(self, text, self.get_cursor_location())
        self.undo_manager.push(insert_cmd)

    def _internal_insert_text(self, text, location):
        lines_to_insert = text.split('\n')
        current_line = self.lines[location.row]
        
        tail = current_line[location.column:]
        self.lines[location.row] = current_line[:location.column]  # insert at cursor position
        
        self.lines[location.row] += lines_to_insert[0]
        
        end_location = Location(location.row, len(self.lines[location.row]))

        if len(lines_to_insert) > 1:  # if there are multiple lines to insert
            for i in range(1, len(lines_to_insert)):
                self.lines.insert(location.row + i, lines_to_insert[i])
            
            end_row = location.row + len(lines_to_insert) - 1
            self.lines[end_row] += tail
            end_location = Location(end_row, len(lines_to_insert[-1]))
        else:  # if only one line to insert
            self.lines[location.row] += tail
        
        return end_location

    def delete_before(self):
        if not self.selection_range.is_empty():
            delete_cmd = DeleteAction(self, self.selection_range)
            self.undo_manager.push(delete_cmd)
            return
        
        if self.cursor_location.column == 0 and self.cursor_location.row == 0:
            return

        end_delete = self.get_cursor_location()
      
        start_row = end_delete.row
        start_col = end_delete.column
        
        if start_col > 0:
            start_col -= 1
        else:
            start_row -= 1
            start_col = len(self.lines[start_row])

        start_delete = Location(start_row, start_col)
        delete_cmd = DeleteAction(self, LocationRange(start_delete, end_delete))
        self.undo_manager.push(delete_cmd)

    def delete_after(self):
        if not self.selection_range.is_empty():
            delete_cmd = DeleteAction(self, self.selection_range)
            self.undo_manager.push(delete_cmd)
            return
        
        start_delete = self.get_cursor_location()
        
        # Check if at the very end of the document
        if start_delete.column == len(self.lines[start_delete.row]) and start_delete.row == len(self.lines) - 1:
            return 
    
        end_row = start_delete.row
        end_col = start_delete.column

        if end_col < len(self.lines[end_row]):
            end_col += 1
        else: # End of a line, move to the start of the next one
            end_row += 1
            end_col = 0
            
        end_delete = Location(end_row, end_col)
        delete_cmd = DeleteAction(self, LocationRange(start_delete, end_delete))
        self.undo_manager.push(delete_cmd)

    def _internal_delete_range(self, r: LocationRange):
        if r.is_empty(): return

        start, end = r.start, r.end
        first_line_part = self.lines[start.row][:start.column]
        last_line_part = self.lines[end.row][end.column:]
        self.lines[start.row] = first_line_part + last_line_part
        if end.row > start.row:
            del self.lines[start.row + 1 : end.row + 1]
        self.set_cursor_location(start)
        self.set_selection_range(start, start)

    def clear_document(self):
        start_location = Location(0, 0)
        end_location = Location(len(self.lines) - 1, len(self.lines[-1]) if self.lines else 0)

        delete_cmd = DeleteAction(self, LocationRange(start_location, end_location))
        self.undo_manager.push(delete_cmd)
        