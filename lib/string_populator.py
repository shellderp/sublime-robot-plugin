import sublime

from robot.api import TestCaseFile
from robot.parsing.populators import FromFilePopulator

class FromStringPopulator(FromFilePopulator):
    def __init__(self, datafile, lines):
        super(FromStringPopulator, self).__init__(datafile)
        self.lines = lines

    def readlines(self):
        return self.lines

    def close(self):
        pass

    def _open(self, path):
        return self

def populate_testcase_file(view):
    regions = view.split_by_newlines(sublime.Region(0, view.size()))
    lines = [view.substr(region).encode('ascii', 'replace') + '\n' for region in regions]
    test_case_file = TestCaseFile(source=view.file_name())
    FromStringPopulator(test_case_file, lines).populate(test_case_file.source)
    return test_case_file

def populate_from_lines(lines, file_path):
    data_file = TestCaseFile(source=file_path)
    FromStringPopulator(data_file, lines).populate(file_path)
    return data_file
