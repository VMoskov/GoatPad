from observers.clipboard.clipboard_observer import ClipboardObserver


class ClipboardStack:
    def __init__(self):
        self.texts = []
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update_clipboard()

    def push(self, text):
        # add text to the top of the stack
        self.texts.append(text)
        self.notify_observers()

    def pop(self):
        # removes and returns the text from the top of the stack
        if self.is_empty():
            raise IndexError('pop from empty clipboard stack')
        text = self.texts.pop()
        self.notify_observers()
        return text

    def peek(self):
        # returns the text from the top of the stack without removing it
        if self.is_empty():
            raise IndexError('peek from empty clipboard stack')
        return self.texts[-1]

    def is_empty(self):
        return not self.texts

    def clear(self):
        # clears the clipboard stack
        self.texts.clear()
        self.notify_observers()