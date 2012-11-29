import os
from copy import copy
from collections import deque
from time import time

import sublime

from robot.api import TestCaseFile, ResourceFile
from robot.errors import DataError

from scanner_cache import ScannerCache


scanner_cache = ScannerCache()

SCAN_TIMEOUT = 5 # seconds

def __scan_file(view, keywords, data_file, import_history, start_time):
    if time() - start_time > SCAN_TIMEOUT:
        sublime.set_timeout(lambda: view.set_status('scan_error', 'scanning timeout exceeded'), 0)
        sublime.set_timeout(lambda: view.erase_status('scan_error'), 5000)
        return
    if data_file.source in import_history:
        # prevent circular import loops
        return
    import_history = copy(import_history)
    import_history.append(data_file.source)

    for setting in data_file.imports:
        if hasattr(setting, 'type'):
            if setting.type == 'Resource':
                resource_path = os.path.normpath(os.path.join(setting.directory, setting.name))
                cached = scanner_cache.get_cached_data(resource_path)
                if cached:
                    __scan_file(view, keywords, cached, import_history, start_time)
                else:
                    try:
                        resource_data = ResourceFile(source=resource_path).populate()
                        scanner_cache.put_data(resource_path, resource_data)
                        __scan_file(view, keywords, resource_data, import_history, start_time)
                    except DataError as de:
                        print 'error reading resource:', resource_path

    for keyword in data_file.keyword_table:
        keywords[keyword.name.lower()] = keyword

def scan_file(view, data_file):
    keywords = {}
    __scan_file(view, keywords, data_file, deque(), time())
    return keywords
