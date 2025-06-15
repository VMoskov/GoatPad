import tkinter as tk
from tkinter import messagebox
import sys
import os

root_directory = '.'
sys.path.append(root_directory)
for dirpath, dirnames, filenames in os.walk(root_directory):
    if dirpath not in sys.path:
        sys.path.append(dirpath)

from text_editor_model import TextEditorModel
from observers.cursor.curser_observer import CursorObserver
from observers.text.text_observer import TextObserver
from position.location import Location
from position.location_range import LocationRange
from clipboard.clipboard_stack import ClipboardStack
from observers.clipboard.clipboard_observer import ClipboardObserver
from stack.undo_manager import UndoManager
from observers.stack.undo_manager_observer import UndoManagerObserver
from commands.delete_action import DeleteAction


class TextEditor(tk.Frame, CursorObserver, TextObserver):
    def __init__(self, parent, model: TextEditorModel, clipboard: ClipboardStack, undo_manager: UndoManager, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        
        self.model = model
        self.clipboard = clipboard
        self.undo_manager = undo_manager
        
        self.model.add_cursor_observer(self)
        self.model.add_text_observer(self)

        self.selection_anchor = None
        
        self.font_family = 'Courier'
        self.font_size = 14
        self.line_height = self.font_size + 4
        self.char_width = 8  # approx. width of character
        self.padding = 5
        self.selection_color = '#d2e4ff'

        self.canvas = tk.Canvas(self, bg='white', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        self.bind_keys()
        self.canvas.focus_set()
        self.redraw()

    def bind_keys(self):
        modifier = 'Command' if sys.platform == 'darwin' else 'Control'  # Mac uses Command, others use Control
        
        # --- Cursor movement bindings ---
        self.canvas.bind('<Up>', self.handle_regular_movement)
        self.canvas.bind('<Down>', self.handle_regular_movement)
        self.canvas.bind('<Left>', self.handle_regular_movement)
        self.canvas.bind('<Right>', self.handle_regular_movement)

        # --- Selection bindings ---
        self.canvas.bind('<Shift-Up>', lambda e: self.handle_shift_movement(self.model.do_move_up))
        self.canvas.bind('<Shift-Down>', lambda e: self.handle_shift_movement(self.model.do_move_down))
        self.canvas.bind('<Shift-Left>', lambda e: self.handle_shift_movement(self.model.do_move_left))
        self.canvas.bind('<Shift-Right>', lambda e: self.handle_shift_movement(self.model.do_move_right))
        self.canvas.bind(f'<{modifier}-a>', lambda e: self.model.select_all())

        # --- Key press bindings ---
        self.canvas.bind('<Key>', self.handle_key_press)
        self.canvas.bind('<Return>', self.handle_key_press)
        self.canvas.bind('<BackSpace>', lambda e: self.model.delete_before())
        self.canvas.bind('<Delete>', lambda e: self.model.delete_after())
        
        # --- Clipboard operations ---
        self.canvas.bind(f'<{modifier}-c>', self.handle_copy)
        self.canvas.bind(f'<{modifier}-x>', self.handle_cut)
        self.canvas.bind(f'<{modifier}-v>', self.handle_paste)
        self.canvas.bind(f'<{modifier}-Shift-V>', self.handle_paste_and_pop)
        
        # --- Undo/Redo operations ---
        self.canvas.bind(f'<{modifier}-z>', lambda e: self.undo_manager.undo())
        self.canvas.bind(f'<{modifier}-y>', lambda e: self.undo_manager.redo())
        self.canvas.bind(f'<{modifier}-Shift-Z>', lambda e: self.undo_manager.redo())

        # --- Close the application ---
        self.canvas.bind('<Escape>', lambda e: self.master.quit())
        

    # --- Event handlers for clipboard operations ---
    def handle_copy(self, event=None):
        selection = self.model.get_selection_range()
        if not selection.is_empty():
            text = self.model.get_text_from_range(selection)
            self.clipboard.push(text)
            self.selection_anchor = None

    def handle_cut(self, event=None):
        selection = self.model.get_selection_range()
        if not selection.is_empty():
            text = self.model.get_text_from_range(selection)
            self.clipboard.push(text)
            delete_cmd = DeleteAction(self.model, selection)
            self.undo_manager.push(delete_cmd)
            self.selection_anchor = None

    def handle_paste(self, event=None):
        if not self.clipboard.is_empty():
            self.model.insert(self.clipboard.peek())

    def handle_paste_and_pop(self, event=None):
        if not self.clipboard.is_empty():
            self.model.insert(self.clipboard.pop())

    def handle_regular_movement(self, event):
        self.selection_anchor = None
        if event.keysym == 'Up': self.model.move_cursor_up()
        elif event.keysym == 'Down': self.model.move_cursor_down()
        elif event.keysym == 'Left': self.model.move_cursor_left()
        elif event.keysym == 'Right': self.model.move_cursor_right()

    def handle_shift_movement(self, move_action):
        if self.selection_anchor is None:
            current_loc = self.model.get_cursor_location()
            self.selection_anchor = Location(row=current_loc.row, column=current_loc.column)
        move_action()
        new_location = self.model.get_cursor_location()
        self.model.set_selection_range(start=self.selection_anchor, end=new_location)

    def handle_key_press(self, event):
        self.selection_anchor = None
        if event.keysym in ('Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R', 'Caps_Lock', 'Tab', 'Meta_L', 'Meta_R'):
            return
        char_to_insert = '\n' if event.keysym == 'Return' else event.char
        if char_to_insert:
            self.model.insert(char_to_insert)

    def redraw(self, cursor_location=None):
        if cursor_location is None: cursor_location = self.model.get_cursor_location()
        self.canvas.delete('all')
        selection = self.model.get_selection_range()

        for i, line in enumerate(self.model.all_lines()):
            y_pos = i * self.line_height + self.padding

            if not selection.is_empty() and selection.start.row <= i <= selection.end.row:
                start_col = selection.start.column if i == selection.start.row else 0
                end_col = selection.end.column if i == selection.end.row else len(line)
                x_start = self.padding + start_col * self.char_width
                x_end = self.padding + end_col * self.char_width
                # draw selection rectangle
                self.canvas.create_rectangle(x_start, y_pos, 
                                             x_end, y_pos + self.line_height, 
                                             fill=self.selection_color, 
                                             outline=''
                                             )
            # draw text
            self.canvas.create_text(self.padding, 
                                    y_pos, 
                                    text=line, 
                                    anchor='nw', 
                                    font=(self.font_family, self.font_size), 
                                    fill='black'
                                    )
        # draw cursor
        cursor_x = self.padding + cursor_location.column * self.char_width
        cursor_y_start = cursor_location.row * self.line_height + self.padding
        cursor_y_end = cursor_y_start + self.line_height
        self.canvas.create_line(cursor_x, cursor_y_start, cursor_x, cursor_y_end, fill='blue', width=2)

    # --- Observer metode ---
    def update_cursor_location(self, location: Location):
        self.redraw(cursor_location=location)
        self.master.update_ui_state()  # notify main window to update buttons

    def update_text(self):
        self.redraw(cursor_location=self.model.get_cursor_location())
        self.master.update_ui_state() # notify main window to update buttons
