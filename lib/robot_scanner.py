import os
from copy import copy
from collections import deque
from time import time

from robot.api import TestCaseFile, ResourceFile
from robot.errors import DataError

from scanner_cache import ScannerCache


scanner_cache = ScannerCache()

SCAN_TIMEOUT = 5 # seconds

def __scan_file(keywords, data_file, import_history, start_time):
    if (time() - start_time > SCAN_TIMEOUT):
        print 'scanning timeout exceeded', time(), start_time
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
                    __scan_file(keywords, cached, import_history, start_time)
                else:
                    try:
                        resource_data = ResourceFile(source=resource_path).populate()
                        scanner_cache.put_data(resource_path, resource_data)
                        __scan_file(keywords, resource_data, import_history, start_time)
                    except DataError as de:
                        print 'error reading resource:', resource_path, de

    for keyword in data_file.keyword_table:
        keywords[keyword.name.lower()] = keyword

def scan_file(data_file):
    keywords = {}
    __scan_file(keywords, data_file, deque(), time())
    return keywords
