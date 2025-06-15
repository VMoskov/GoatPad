# commands/uppercase_action.py
from edit_action import EditAction


class UpperCaseAction(EditAction):
    def __init__(self, model):
        self.model = model
        self.previous_text = self.model.get_text()  # save the original text

    def execute_do(self):
        original_text = self.model.get_text()

        new_text = original_text.title()
        self.model.set_text(new_text)
        self.model.notify_text_observers()
        self.model.notify_cursor_observers()

    def execute_undo(self):
        # Vrati dokument na originalno stanje
        self.model.set_text(self.previous_text)
        self.model.notify_text_observers()
        self.model.notify_cursor_observers()