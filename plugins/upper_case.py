from plugin import Plugin
from commands.upper_case_action import UpperCaseAction


class UpperCasePlugin(Plugin):
    def get_name(self):
        return 'Upper Case'

    def get_description(self):
        return 'Converts the selected text to upper case.'

    def execute(self, model, undo_manager, clipboard):
        command = UpperCaseAction(model)
        undo_manager.push(command)