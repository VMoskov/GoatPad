from plugin import Plugin
from tkinter import messagebox


class StatisticsPlugin(Plugin):
    def get_name(self):
        return 'Statistics'

    def get_description(self):
        return 'Calculates statistics of the text, such as word count and character count.'

    def execute(self, model, undo_manager, clipboard):
        text = model.get_text()
        
        line_count = len(model.lines)
        word_count = len(text.split())
        char_count = len(text)
        
        message = (
            f'Num rows: {line_count}\n'
            f'Num words: {word_count}\n'
            f'Num chars: {char_count}'
        )
        
        messagebox.showinfo('Document statistics', message)


if __name__ == '__main__':
    plugin = StatisticsPlugin()
    print(plugin.get_name())
    print(plugin.get_description())
    # Note: The execute method requires a model, undo_manager, and clipboard to function properly.
    # These would typically be provided by the main application context.
    # check parent class for our StatisticsPlugin class
    print(plugin.__class__.__bases__)
    print(plugin.__class__.__bases__[0])  # Should print 'Plugin'
    print(Plugin)