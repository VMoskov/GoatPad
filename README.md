# GoatPad - Text Editor for real Goats

GoatPad is a comprehensive text editor application built using Python's standard Tkinter library. It was developed as a project to explore and implement several core software design patterns in a practical, hands-on application.

## Features

- **Full Text Editing Suite:** Supports standard text insertion and deletion.
- **Advanced Selection:** Text selection using Shift + Arrow Keys.
- **File Operations:** Open and save text files (`.txt`).
- **Undo/Redo System:** Multi-level undo and redo functionality for all text-modifying actions, managed by a central `UndoManager`.
- **Custom Clipboard:** Features a stack-based clipboard with support for:
  - **Copy** (`Ctrl+C` or `Cmd+C`)
  - **Cut** (`Ctrl+X` or `Cmd+X`)
  - **Paste** (`Ctrl+V` or `Cmd+V`) - Peeks at the top item without removing it.
  - **Paste and Take** (`Ctrl+Shift+V`) - Pastes the top item and removes it from the clipboard stack.
- **Dynamic Plugin System:** Extend the editor's functionality by simply dropping new Python files into the `plugins/` directory.
- **Rich User Interface:**
  - A full menu bar (`File`, `Edit`, `Move`, `Plugins`).
  - A quick-access toolbar for common actions.
  - A status bar displaying cursor position and total line count.
- **State-Aware UI:** Toolbar buttons and menu items are dynamically enabled or disabled based on the current context (e.g., "Paste" is disabled if the clipboard is empty, "Undo" is disabled if there's nothing to undo).

## Design Patterns Implemented

A key goal of this project was the practical application of software design patterns. The following patterns are central to its architecture:

-   **Command Pattern:** All actions that modify the document (inserting text, deleting text, etc.) are encapsulated as `EditAction` objects. This decouples the execution of a command from the UI and is the foundation of the undo/redo system.
-   **Observer Pattern:** The UI is decoupled from the data models. The main application window acts as an "Observer" to multiple "Subjects" (`UndoManager`, `ClipboardStack`, `TextEditorModel`). When the state of a subject changes, the UI is automatically notified and updates itself accordingly (e.g., enabling/disabling the "Undo" button).
-   **Singleton Pattern:** The `UndoManager` is implemented as a singleton to ensure there is only one central history of commands for the entire application.
-   **Plugin (Strategy/Interface) Pattern:** A `Plugin` abstract base class defines a common interface for all extensions. The main application dynamically loads any class that implements this interface, allowing for new functionality without changing the core application code.

## Project Structure

The project is organized into packages to separate concerns:

```
notepad_project/
├── notepad.py              # Main application file (creates window, UI)
├── text_editor.py          # The core TextEditor widget
├── text_editor_model.py    # The data model for the text
│
├── plugin_interface.py     # Defines the abstract Plugin class
│
├── plugins/
│   ├── __init__.py
│   ├── statistics_plugin.py
│   └── uppercase_plugin.py
│
├── commands/
│   ├── __init__.py
│   ├── edit_action.py      # Abstract command class
│   ├── delete_action.py
│   ├── insert_text_action.py
│   └── uppercase_action.py
│
├── undo/
│   ├── __init__.py
│   ├── undo_manager.py
│   └── undo_manager_observer.py
│
├── clipboard/
│   ├── __init__.py
│   ├── clipboard_stack.py
│   └── clipboard_observer.py
│
├── observers/
│   ├── __init__.py
│   ├── ... (subdirectories for other observers)
│
└── position/
    ├── __init__.py
    ├── location.py
    └── location_range.py
```

## How to Run

1.  Ensure you have Python 3 installed. Tkinter is included by default with most Python installations.
2.  Arrange all files and directories according to the structure shown above.
3.  Run the main application file (e.g., `notepad.py`) from your terminal from the project's root directory:
    ```bash
    python notepad.py
    ```

## How to Create a New Plugin

The application's functionality can be easily extended.

1.  Create a new Python file inside the `plugins/` directory (e.g., `my_plugin.py`).
2.  Inside the file, create a class that inherits from the `Plugin` interface.
3.  Implement the three required methods: `getName()`, `getDescription()`, and `execute()`.
4.  Run the main application. Your new plugin will automatically appear in the "Plugins" menu.

### Example: "Hello World" Plugin

```python
# plugins/hello_plugin.py

from tkinter import messagebox
# Use relative import to get the interface
from ..plugin_interface import Plugin
from ..text_editor_model import TextEditorModel
from ..undo.undo_manager import UndoManager
from ..clipboard.clipboard_stack import ClipboardStack

class HelloWorldPlugin(Plugin):
    def getName(self) -> str:
        return "Hello World"

    def getDescription(self) -> str:
        return "A simple plugin that shows a greeting."

    def execute(self, model: TextEditorModel, undo_manager: UndoManager, clipboard: Stack):
        # This plugin doesn't modify the text, so it doesn't need the undo_manager.
        messagebox.showinfo("Hello", "Hello, World!")
