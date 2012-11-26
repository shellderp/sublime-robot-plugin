import hashlib

class CacheEntry:
    def __init__(self, stored_hash, data):
        self.stored_hash = stored_hash
        self.data = data

class ScannerCache:
    def __init__(self):
        self.cache = {}

    def compute_hash(self, file_path):
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                 md5.update(chunk)
        return md5.digest()

    def get_cached_data(self, file_path):
        if not file_path in self.cache:
            return None
        entry = self.cache[file_path]
        try:
            current_hash = self.compute_hash(file_path)
        except IOError:
            # file is probably deleted, so remove the cached entry
            del self.cache[file_path]
            return None
        if entry.stored_hash != current_hash:
            return None
        return entry.data

    def put_data(self, file_path, data):
        self.cache[file_path] = CacheEntry(self.compute_hash(file_path), data)
