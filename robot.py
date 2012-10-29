import sublime, sublime_plugin
import os, functools
from keyword_parse import get_keyword_at_pos
from robot.parsing import *

# only available when the plugin is being loaded
plugin_dir = os.getcwd()

keywords = {}

# working_dir is the directory that contains the file to be parsed
def parse_file(working_dir, line_gen):

    for line in line_gen():
        stripped = line.strip()
        if stripped.startswith('Resource'):
            resource = line[line.find('Resource') + 8:].strip()
            resource_path = os.path.join(working_dir, resource)
            new_working_dir, __file_path = os.path.split(resource_path)
            parse_file(new_working_dir, functools.partial(file_line_gen, resource_path))
        elif stripped.startswith('*'):
            print 'mode change:', stripped


def view_line_gen(view):
    regions = view.split_by_newlines(sublime.Region(0, view.size()))
    for region in regions:
        yield view.substr(region)

def file_line_gen(file_path):
    try:
        with open(file_path) as f:
            for line in f:
                yield line
    except IOError as e:
        print 'Opening file failed:', e

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
        
        if keyword is None:
            return

        print 'searching for keyword:', keyword

        init_txt_path = os.path.join(path, '__init__.txt')
        if os.path.exists(init_txt_path):
            parse_file(path, functools.partial(file_line_gen, init_txt_path))

        # we have the keyword we're going to look for, now parse the file
        parse_file(path, functools.partial(view_line_gen, view))

        #window.open_file("%s:%d" % (resource_path, 10), sublime.ENCODED_POSITION)


class AutoSyntaxHighlight(sublime_plugin.EventListener):
    def on_load(self, view):
        if (view.file_name().endswith('.txt') and
            view.find('\*{3}\s*(settings|keywords|test cases|variables)\s*\*{3}', 0, sublime.IGNORECASE) != None):

            view.set_syntax_file(os.path.join(plugin_dir, "robot.tmLanguage"))
