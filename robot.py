import sublime, sublime_plugin
import os


def get_keyword_at_pos(line, col):
    if len(line) == 0:
        return None

    # first look back until we find 2 spaces in a row, or reach the beginning
    i = col - 1
    while i > 0:
        print "lookbehind at", i, "=", line[i]
        if line[i - 1] == "\t" or (line[i - 1] == " " and len(line) > i and line[i] == " "):
            i = i + 1
            break
        i -= 1

    begin = i

    # now look forward or until the end
    i = col # previous included line[col]
    for i in range(col + 1, len(line), 1):
        print "lookahead at", i, "=", line[i]
        if line[i] == "\t" or (line[i] == " " and len(line) > i and line[i + 1] == " "):
            i = i - 1
            break
    end = i
    print begin, end
    keyword = line[begin:end]
    if len(keyword) == 0:
        return None
    return line[begin:end]

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
        print keyword
        
        #window.open_file("%s:%d" % (resource_path, 10), sublime.ENCODED_POSITION)


class AutoSyntaxHighlight(sublime_plugin.EventListener):
    def on_load(self, view):
        if (view.file_name().endswith('.txt') and
            view.find('\*{3}\s*settings\s*\*{3}', 0, sublime.IGNORECASE) != None):

            view.set_syntax_file(os.path.join(sublime.packages_path(), "sublime-robot-plugin/robot.tmLanguage"))
