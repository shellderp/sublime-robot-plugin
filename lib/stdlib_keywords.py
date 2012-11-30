import os
import json
import webbrowser
import urllib

keywords = {}

def load(plugin_dir):
    keywords.clear()

    scan_dir = os.path.join(plugin_dir, 'stdlib_keywords')
    for root, dirs, files in os.walk(scan_dir):
        for file_path in filter(lambda f: f.endswith('.json'), files):
            file_path = os.path.join(root, file_path)
            with open(file_path, 'rb') as f:
                json_dict = json.load(f)
                url = json_dict['url']
                for keyword in json_dict['keywords']:
                    keywords[keyword.lower()] = url + '#' + urllib.quote(keyword)

def show_if_exists(lower_name):
    if not keywords.has_key(lower_name):
        return False

    return webbrowser.open(keywords[lower_name])
