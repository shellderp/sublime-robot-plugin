import os, sys
lib_path = os.path.normpath(os.path.join(os.getcwd(), 'lib/'))
if lib_path not in sys.path:
    sys.path.append(lib_path)
pyd_path = os.path.dirname(sys.executable)
if pyd_path not in sys.path:
    sys.path.append(pyd_path)

import sublime, sublime_plugin
from keyword_parse import get_keyword_at_pos
from robot.api import TestCaseFile, ResourceFile
from robot.errors import DataError
from string_populator import FromStringPopulator

# only available when the plugin is being loaded
plugin_dir = os.getcwd()

keywords = []

# data_file is an already loaded robot file
def parse_file(data_file):
    for setting in data_file.setting_table:
        if hasattr(setting, 'type'):
            if setting.type == 'Resource':
                resource_path = os.path.normpath(os.path.join(setting.directory, setting.name))
                try:
                    parse_file(ResourceFile(source=resource_path).populate())
                except DataError as de:
                    print 'error reading resource:', resource_path, de

    for keyword in data_file.keyword_table:
        keywords.append(keyword)

views_to_center = {}

def open_keyword_file(window, keyword):
    source_path = keyword.source
    new_view = window.open_file("%s:%d" % (source_path, keyword.linenumber), sublime.ENCODED_POSITION)
    new_view.show_at_center(new_view.text_point(keyword.linenumber, 0))
    if new_view.is_loading():
        views_to_center[new_view.id()] = keyword.linenumber

def is_robot_format(view):
    return view.settings().get('syntax').endswith('robot.tmLanguage')

def populate_testcase_file(view):
    regions = view.split_by_newlines(sublime.Region(0, view.size()))
    lines = [view.substr(region).encode('ascii', 'replace') + '\n' for region in regions]
    test_case_file = TestCaseFile(source=view.file_name())
    FromStringPopulator(test_case_file, lines).populate(test_case_file.source)
    return test_case_file

def find_keyword(name):
    lower_name = name.lower()
    for keyword in keywords:
        # todo support regex + ignore whitespace
        if lower_name == keyword.name.lower():
            return keyword

class RobotGoToKeywordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        window = view.window()

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
            window.open_file(resource_path)
            return

        keyword = get_keyword_at_pos(line, col)
        if not keyword:
            return

        del keywords[:]
        parse_file(populate_testcase_file(view))

        for bdd_prefix in ['given ', 'and ', 'when ', 'then ']:
            if keyword.lower().startswith(bdd_prefix):
                substr = keyword[len(bdd_prefix):]
                kw = find_keyword(substr)
                if kw:
                    open_keyword_file(window, kw)
                    break
        else:
            kw = find_keyword(keyword)
            if kw:
                open_keyword_file(window, kw)


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

            del keywords[:]
            parse_file(populate_testcase_file(view))
            user_keywords = [(keyword.name, keyword.name) for keyword in keywords if keyword.name.startswith(prefix)]
            
            return user_keywords
