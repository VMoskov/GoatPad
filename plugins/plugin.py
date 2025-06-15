from abc import ABC, abstractmethod

class Plugin(ABC):
    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_description(self):
        pass

    @abstractmethod
    def execute(self, model, undo_manager, clipboard):
        pass