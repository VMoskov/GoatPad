
from .edit_action import EditAction
from position.location_range import LocationRange

class InsertTextAction(EditAction):
    def __init__(self, model, text, location):
        self.model = model
        self.text_to_insert = text
        self.insert_location = location
        self.end_location = None

    def execute_do(self):
        self.end_location = self.model._internal_insert_text(self.text_to_insert, self.insert_location)
        self.model.set_cursor_location(self.end_location)
        self.model.notify_text_observers()
        self.model.notify_cursor_observers()

    def execute_undo(self):
        # delete the inserted text
        undo_range = LocationRange(self.insert_location, self.end_location)
        self.model._internal_delete_range(undo_range)
        self.model.set_cursor_location(self.insert_location)
        self.model.notify_text_observers()
        self.model.notify_cursor_observers()