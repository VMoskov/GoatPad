from abc import ABC, abstractmethod

class TextObserver(ABC):
    @abstractmethod
    def update_text(self):
        pass