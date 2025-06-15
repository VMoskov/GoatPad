from .edit_action import EditAction


class DeleteAction(EditAction):
    def __init__(self, model, selection_range):
        self.model = model
        self.selection_range = selection_range
        # before deleting, we store the text that will be deleted
        self.deleted_text = self.model.get_text_from_range(self.selection_range)
        self.start_location = self.selection_range.start

    def execute_do(self):
        self.model._internal_delete_range(self.selection_range)
        self.model.notify_text_observers()
        self.model.notify_cursor_observers()

    def execute_undo(self):
        # to undo the delete, we reinsert the deleted text at the original location
        self.model._internal_insert_text(self.deleted_text, self.start_location)
        self.model.set_cursor_location(self.selection_range.end)
        self.model.notify_text_observers()
        self.model.notify_cursor_observers()