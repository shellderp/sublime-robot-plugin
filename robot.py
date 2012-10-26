import sublime, sublime_plugin
import os
from keyword_parse import get_keyword_at_pos

# only available when the plugin is being loaded
plugin_dir = os.getcwd()

class RobotGoToKeywordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        window = view.window()

        if not view.settings().get('syntax').endswith('robot.tmLanguage'):
            return # don't run for non-robot files

        sel = view.sel()[0]
        line = view.substr(view.line(sel))
        row, col = view.rowcol(sel.begin())
        
        file_path = view.file_name()
        if file_path is None:
            sublime.error_message('Please save the buffer to a file first.')
            return
        path, file_name = os.path.split(file_path)

        if line.strip().startswith('Resource'):
            resource = line[line.find('Resource') + 8:].strip()
            resource_path = os.path.join(path, resource)
            window.open_file(resource_path)
            return

        keyword = get_keyword_at_pos(line, col)
        print keyword
        
        #window.open_file("%s:%d" % (resource_path, 10), sublime.ENCODED_POSITION)


class AutoSyntaxHighlight(sublime_plugin.EventListener):
    def on_load(self, view):
        if (view.file_name().endswith('.txt') and
            view.find('\*{3}\s*(settings|keywords|test cases|variables)\s*\*{3}', 0, sublime.IGNORECASE) != None):

            view.set_syntax_file(os.path.join(plugin_dir, "robot.tmLanguage"))
