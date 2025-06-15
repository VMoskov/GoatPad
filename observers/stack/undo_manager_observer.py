from abc import ABC, abstractmethod

class UndoManagerObserver(ABC):
    @abstractmethod
    def update_undo_stack(self, is_empty: bool):
        pass
    
    @abstractmethod
    def update_redo_stack(self, is_empty: bool):
        pass