import os
import json
import webbrowser
import urllib


keywords = {}

class WebKeyword:
    def __init__(self, name, url, library_name, args, doc):
        self.name = library_name + '.' + name
        self.url = url
        self.description = [args, doc, url]

    def show_definition(self, view, views_to_center):
        webbrowser.open(self.url)

    def allow_unprompted_go_to(self):
        # Opening the browser would be inconvenient if the user misclicked
        return False


def load(plugin_dir):
    keywords.clear()

    scan_dir = os.path.join(plugin_dir, 'stdlib_keywords')
    for root, dirs, files in os.walk(scan_dir):
        for file_path in filter(lambda f: f.endswith('.json'), files):
            library_name = file_path[:-5]
            file_path = os.path.join(root, file_path)
            with open(file_path, 'rb') as f:
                json_dict = json.load(f)
                url = json_dict['url']
                for keyword in json_dict['keywords']:
                    name = keyword['name']
                    args = keyword['args']
                    doc = keyword['shortdoc']
                    lower_name = name.lower()
                    web_keyword = WebKeyword(name, url + '#' + urllib.quote(name), library_name, args, doc)
                    if not keywords.has_key(lower_name):
                        keywords[lower_name] = []
                    keywords[lower_name].append(web_keyword)


def search_keywords(name):
    lower_name = name.lower()
    if not keywords.has_key(lower_name):
        return []

    return keywords[lower_name]
