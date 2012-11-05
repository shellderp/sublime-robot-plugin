import os, sys
lib_path = os.path.normpath(os.path.join(os.getcwd(), 'lib/'))
if lib_path not in sys.path:
    sys.path.append(lib_path)
pyd_path = os.path.dirname(sys.executable)
if pyd_path not in sys.path:
    sys.path.append(pyd_path)

import sublime, sublime_plugin
from keyword_parse import get_keyword_at_pos
#import robot.utils
from robot.parsing import TestCaseFile, ResourceFile
from string_populator import FromStringPopulator
import inspect

# only available when the plugin is being loaded
plugin_dir = os.getcwd()

keywords = {}

# suite is an already loaded suite
def parse_file(suite):
    for setting in suite.setting_table:
        if hasattr(setting, 'type'):
            if setting.type == 'Resource':
                resource_path = os.path.join(setting.directory, setting.name)
                parse_file(ResourceFile(source=resource_path).populate())

    ### not concerned with testcases ATM
    # for test in suite.testcase_table:
    #     print test.name
    #     for setting in test.settings:
    #         print '\t', setting.setting_name, setting.value if hasattr(setting, 'value') else ''
    #     for step in test.steps:
    #         print '\t', step.keyword, step.args

    for keyword in suite.keyword_table:
        keywords[keyword.name] = keyword
        #print keyword.name
        # for setting in keyword.settings:
        #     print '\t', setting.setting_name, setting.value if hasattr(setting, 'value') else ''
        #for step in keyword.steps:
         #   print '\t', step.keyword, step.args

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

        # populate a TestCaseFile from the lines in the buffer
        regions = view.split_by_newlines(sublime.Region(0, view.size()))
        lines = [view.substr(region).encode('ascii', 'replace') + '\n' for region in regions]
        suite = TestCaseFile(source=file_path)
        FromStringPopulator(suite, lines).populate(suite.source)
        suite._validate()

        keywords.clear()
        parse_file(suite)
        try:
            for bdd_prefix in ['given ', 'and ', 'when ', 'then ']:
                if keyword.lower().startswith(bdd_prefix):
                    substr = keyword[len(bdd_prefix):]
                    if keywords.has_key(substr):
                        source_path = keywords[substr].source
                        print source_path
                        window.open_file("%s" % (source_path))
                        return
            source_path = keywords[keyword].source
            print source_path
            window.open_file("%s" % (source_path))
        except:
            print 'keyword not found:', keyword

        #window.open_file("%s:%d" % (resource_path, 10), sublime.ENCODED_POSITION)


class AutoSyntaxHighlight(sublime_plugin.EventListener):
    def on_load(self, view):
        if (view.file_name().endswith('.txt') and
            view.find('\*{3}\s*(settings|keywords|test cases|variables)\s*\*{3}', 0, sublime.IGNORECASE) != None):

            view.set_syntax_file(os.path.join(plugin_dir, "robot.tmLanguage"))
