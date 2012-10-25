import sublime, sublime_plugin
import os


def get_keyword_at_pos(line, col):
    if len(line) == 0:
        return None

    # first, look back until we find 2 spaces in a row, or reach the beginning
    i = 0
    for i in range(col, 0, -1):
        print line[i-1]
    
    for i in range(col, len(line), 1):
        print line[i]

class RobotGoToKeywordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        window = view.window()

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

        #resources = view.find_all("^Resource\s+(.+)$") # todo: can resource start with a space? probably..
        #for r in resources:
            #print view.substr(r)
        #print os.path.normpath(os.path.join(path, '../lolrobot.txt'))
        #window.open_file("%s:%d" % (resource_path, 10), sublime.ENCODED_POSITION)


class AutoSyntaxHighlight(sublime_plugin.EventListener):
    def on_load(self, view):
        if (view.file_name().endswith('.txt') and
            view.find('\*{3}\s*settings\s*\*{3}', 0, sublime.IGNORECASE) != None):
            view.set_syntax_file(os.path.join(sublime.packages_path(), "Robot/robot.tmLanguage"))