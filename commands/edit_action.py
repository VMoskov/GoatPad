from abc import ABC, abstractmethod

class EditAction(ABC):
    @abstractmethod
    def execute_do(self):
        # executes the action
        pass

    @abstractmethod
    def execute_undo(self):
        # undoes the action
        pass