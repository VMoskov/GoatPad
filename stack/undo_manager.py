from commands.edit_action import EditAction
from observers.stack.undo_manager_observer import UndoManagerObserver

class UndoManager:
    _instance = None

    def __init__(self):
        if UndoManager._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.undo_stack = []
            self.redo_stack = []
            self.observers = []

    @staticmethod
    def get_instance():
        """Statička metoda za dohvaćanje jedine instance."""
        if UndoManager._instance is None:
            UndoManager._instance = UndoManager()
        return UndoManager._instance

    # --- Observer methods ---
    def add_observer(self, observer: UndoManagerObserver):
        self.observers.append(observer)

    def remove_observer(self, observer: UndoManagerObserver):
        self.observers.remove(observer)
        
    def notify_observers(self):
        is_undo_empty = not self.undo_stack
        is_redo_empty = not self.redo_stack
        for observer in self.observers:
            observer.update_undo_stack(is_undo_empty)
            observer.update_redo_stack(is_redo_empty)

    # --- Undo/Redo methods ---
    def push(self, command: EditAction):
        self.redo_stack.clear()  # adding a new command clears the redo stack
        command.execute_do()
        self.undo_stack.append(command)
        self.notify_observers()

    def undo(self):
        if not self.undo_stack:
            return
        command = self.undo_stack.pop()
        command.execute_undo()
        self.redo_stack.append(command)
        self.notify_observers()

    def redo(self):
        if not self.redo_stack:
            return
        command = self.redo_stack.pop()
        command.execute_do()
        self.undo_stack.append(command)
        self.notify_observers()