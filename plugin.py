# setup pythonpath to include lib directory before other imports
import os, sys
lib_path = os.path.normpath(os.path.join(os.getcwd(), 'lib'))
if lib_path not in sys.path:
    sys.path.append(lib_path)
pyd_path = os.path.dirname(sys.executable)
if pyd_path not in sys.path:
    sys.path.append(pyd_path)

# only available when the plugin is being loaded
plugin_dir = os.getcwd()

import sublime, sublime_plugin
import threading

from robot.api import TestCaseFile

from keyword_parse import get_keyword_at_pos
from string_populator import FromStringPopulator
from robot_scanner import scan_file

views_to_center = {}

def is_robot_format(view):
    return view.settings().get('syntax').endswith('robot.tmLanguage')

def open_keyword_file(window, keyword):
    source_path = keyword.source
    new_view = window.open_file("%s:%d" % (source_path, keyword.linenumber), sublime.ENCODED_POSITION)
    new_view.show_at_center(new_view.text_point(keyword.linenumber, 0))
    if new_view.is_loading():
        views_to_center[new_view.id()] = keyword.linenumber

def populate_testcase_file(view):
    regions = view.split_by_newlines(sublime.Region(0, view.size()))
    lines = [view.substr(region).encode('ascii', 'replace') + '\n' for region in regions]
    test_case_file = TestCaseFile(source=view.file_name())
    FromStringPopulator(test_case_file, lines).populate(test_case_file.source)
    return test_case_file

def find_keyword(keywords, name):
    lower_name = name.lower()
    if keywords.has_key(lower_name):
        return keywords[lower_name]
    return None

class GoToKeywordThread(threading.Thread):
    def __init__(self, window, view_file, keyword):
        self.window = window
        self.view_file = view_file
        self.keyword = keyword
        threading.Thread.__init__(self)

    def run(self):
        keywords = scan_file(self.view_file)

        for bdd_prefix in ['given ', 'and ', 'when ', 'then ']:
            if self.keyword.lower().startswith(bdd_prefix):
                substr = self.keyword[len(bdd_prefix):]
                kw = find_keyword(keywords, substr)
                if kw:
                    sublime.set_timeout(lambda: open_keyword_file(self.window, kw), 0)
                    break
        else:
            kw = find_keyword(keywords, self.keyword)
            if kw:
                sublime.set_timeout(lambda: open_keyword_file(self.window, kw), 0)

class RobotGoToKeywordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view

        if not is_robot_format(view):
            return

        sel = view.sel()[0]
        line = view.substr(view.line(sel))
        row, col = view.rowcol(sel.begin())

        file_path = view.file_name()
        if not file_path:
            sublime.error_message('Please save the buffer to a file first.')
            return
        path, file_name = os.path.split(file_path)

        if line.strip().startswith('Resource'):
            resource = line[line.find('Resource') + 8:].strip().replace('${CURDIR}', path)
            resource_path = os.path.join(path, resource)
            view.window().open_file(resource_path)
            return

        keyword = get_keyword_at_pos(line, col)
        if not keyword:
            return

        view_file = populate_testcase_file(self.view)
        GoToKeywordThread(view.window(), view_file, keyword).start()


class AutoSyntaxHighlight(sublime_plugin.EventListener):
    def autodetect(self, view):
        # file name can be None if it's a find result view that is restored on startup
        if (view.file_name() != None and view.file_name().endswith('.txt') and
            view.find('\*+\s*(settings?|metadata|(user )?keywords?|test cases?|variables?)', 0, sublime.IGNORECASE) != None):

            view.set_syntax_file(os.path.join(plugin_dir, "robot.tmLanguage"))

    def on_load(self, view):
        if view.id() in views_to_center:
            view.show_at_center(view.text_point(views_to_center[view.id()], 0))
            del views_to_center[view.id()]
        self.autodetect(view)

    def on_post_save(self, view):
        self.autodetect(view)


class AutoComplete(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if is_robot_format(view):
            view_file = populate_testcase_file(view)
            keywords = scan_file(view_file)
            lower_prefix = prefix.lower()
            user_keywords = [(kw.name, kw.name) for kw in keywords.itervalues()
                                if kw.name.lower().startswith(lower_prefix)]
            return user_keywords
