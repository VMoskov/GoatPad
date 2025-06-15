import tkinter as tk
from tkinter import messagebox, filedialog
import sys
import os
import importlib
import inspect

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from editor.text_editor_model import TextEditorModel
from editor.text_editor import TextEditor
from clipboard.clipboard_stack import ClipboardStack
from observers.clipboard.clipboard_observer import ClipboardObserver
from stack.undo_manager import UndoManager
from observers.stack.undo_manager_observer import UndoManagerObserver
from plugins.plugin import Plugin


class Notepad(tk.Tk, UndoManagerObserver, ClipboardObserver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title('GoatPad - A Notepad for real Goats')
        self.geometry('800x600')

        self.plugins = []
        self.load_plugins()

        # model initialization
        self.model = TextEditorModel('A faza, stakla puna mraza\nDimi se zaza u limuzini nazad')
        # self.model = TextEditorModel('This is a sample text for the Notepad application.\nFeel free to edit it as you wish.')
        self.undo_manager = UndoManager.get_instance()
        self.clipboard = ClipboardStack()
        self.text_editor = TextEditor(self, self.model, self.clipboard, self.undo_manager)

        self.create_status_bar()
        self.create_toolbar()
        # text editor initialization
        self.text_editor.pack(side=tk.BOTTOM, fill='both', expand=True)
        
        self.undo_manager.add_observer(self)
        self.clipboard.add_observer(self)

        # UI setup
        self.create_menubar()
        
        self.update_ui_state()

    def create_toolbar(self):
        self.toolbar = tk.Frame(self, bd=1, relief=tk.RAISED)
        
        self.undo_button = tk.Button(self.toolbar, text='Undo', command=self.undo_manager.undo)
        self.undo_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.redo_button = tk.Button(self.toolbar, text='Redo', command=self.undo_manager.redo)
        self.redo_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.cut_button = tk.Button(self.toolbar, text='Cut', command=self.text_editor.handle_cut)
        self.cut_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.copy_button = tk.Button(self.toolbar, text='Copy', command=self.text_editor.handle_copy)
        self.copy_button.pack(side=tk.LEFT, padx=2, pady=2)

        self.paste_button = tk.Button(self.toolbar, text='Paste', command=self.text_editor.handle_paste)
        self.paste_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

    def create_menubar(self):
        menubar = tk.Menu(self)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Open', command=self._handle_open_file)
        file_menu.add_command(label='Save', command=self._handle_save_file)
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.quit)
        menubar.add_cascade(label='File', menu=file_menu)

        self.edit_menu = tk.Menu(menubar, tearoff=0)
        self.edit_menu.add_command(label='Undo', accelerator='Ctrl+Z', command=self.undo_manager.undo)
        self.edit_menu.add_command(label='Redo', accelerator='Ctrl+Y', command=self.undo_manager.redo)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Cut', accelerator='Ctrl+X', command=self.text_editor.handle_cut)
        self.edit_menu.add_command(label='Copy', accelerator='Ctrl+C', command=self.text_editor.handle_copy)
        self.edit_menu.add_command(label='Paste', accelerator='Ctrl+V', command=self.text_editor.handle_paste)
        self.edit_menu.add_command(label='Paste and Take', command=self.text_editor.handle_paste_and_pop)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Delete selection', command=lambda: self.model.delete_after())
        self.edit_menu.add_command(label='Clear document', command=self.model.clear_document)
        menubar.add_cascade(label='Edit', menu=self.edit_menu)

        move_menu = tk.Menu(menubar, tearoff=0)
        move_menu.add_command(label='Cursor to document start', command=self.model.cursor_to_document_start)
        move_menu.add_command(label='Cursor to document end', command=self.model.cursor_to_document_end)
        menubar.add_cascade(label='Move', menu=move_menu)

        if self.plugins:
            plugins_menu = tk.Menu(menubar, tearoff=0)
            for p in self.plugins:
                plugins_menu.add_command(
                    label=p.get_name(),
                    command=lambda p=p: p.execute(self.model, self.undo_manager, self.clipboard)
                )
            menubar.add_cascade(label='Plugins', menu=plugins_menu)

        self.config(menu=menubar)

    def create_status_bar(self):
        self.status_bar = tk.Label(self, text='', bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_ui_state(self):
        # --- Undo/Redo state ---
        undo_state = tk.NORMAL if self.undo_manager.undo_stack else tk.DISABLED
        redo_state = tk.NORMAL if self.undo_manager.redo_stack else tk.DISABLED
        self.undo_button.config(state=undo_state)
        self.edit_menu.entryconfig('Undo', state=undo_state)
        self.redo_button.config(state=redo_state)
        self.edit_menu.entryconfig('Redo', state=redo_state)

        # --- Clipboard state ---
        paste_state = tk.NORMAL if not self.clipboard.is_empty() else tk.DISABLED
        self.paste_button.config(state=paste_state)
        self.edit_menu.entryconfig('Paste', state=paste_state)
        self.edit_menu.entryconfig('Paste and Take', state=paste_state)

        # --- Cut/Copy/Delete state ---
        selection_state = tk.NORMAL if not self.model.get_selection_range().is_empty() else tk.DISABLED
        self.cut_button.config(state=selection_state)
        self.edit_menu.entryconfig('Cut', state=selection_state)
        self.copy_button.config(state=selection_state)
        self.edit_menu.entryconfig('Copy', state=selection_state)
        self.edit_menu.entryconfig('Delete selection', state=selection_state)

        # --- Status bar ---
        cursor_pos = self.model.get_cursor_location()
        line_count = len(self.model.lines)
        status_text = f'Ln {cursor_pos.row + 1}, Col {cursor_pos.column + 1}  |  Lines: {line_count}'
        self.status_bar.config(text=status_text)

    # --- Observer methods ---
    def update_undo_stack(self, is_empty: bool):
        self.update_ui_state()

    def update_redo_stack(self, is_empty: bool):
        self.update_ui_state()

    def update_clipboard(self):
        self.update_ui_state()
        
    # --- File operations ---
    def _handle_open_file(self):
        file_path = filedialog.askopenfilename(defaultextension='.txt',
                                                  filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.model.set_text(content)
            except Exception as e:
                messagebox.showerror('Error', f'Could not open file: {e}')

    def _handle_save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension='.txt',
                                                     filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    content = self.model.get_text()
                    file.write(content)
            except Exception as e:
                messagebox.showerror('Error', f'Could not save file: {e}')

    # --- Plugin loading ---
    def _is_plugin(self, obj):
        return inspect.isclass(obj) and obj.__bases__[0].__name__ == Plugin.__name__

    def load_plugins(self):
        plugins_dir = 'plugins'

        print(f'Loading plugins...')

        for filename in os.listdir(plugins_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = f'{plugins_dir}.{filename[:-3]}'
                try:
                    module = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(module):

                        if self._is_plugin(obj):
                            plugin_instance = obj()  # create an instance of the plugin
                            self.plugins.append(plugin_instance)
                            print(f'Plugin {plugin_instance.get_name()} loaded successfully.')
                except Exception as e:
                    print(f'Failed to load plugin {filename}: {e}')
        
        if not self.plugins:
            print('No plugins found.')
        else:
            print(f'Loaded {len(self.plugins)} plugins.')


if __name__ == '__main__':
    app = Notepad()
    app.mainloop()