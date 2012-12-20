import hashlib

class CacheEntry:
    def __init__(self, stored_hash, data):
        self.stored_hash = stored_hash
        self.data = data

class ScannerCache:
    def __init__(self):
        self.cache = {}

    def compute_hash(self, file_path, preread_lines=None):
        md5 = hashlib.md5()
        if preread_lines is None:
            with open(file_path, 'rb') as f:
                preread_lines = f.readlines()
        for line in preread_lines:
            md5.update(line)
        return md5.digest()

    def get_cached_data(self, file_path, preread_lines=None):
        if not file_path in self.cache:
            return None, None
        entry = self.cache[file_path]
        try:
            current_hash = self.compute_hash(file_path, preread_lines)
        except IOError:
            # file is probably deleted, so remove the cached entry
            del self.cache[file_path]
            return None, None
        if entry.stored_hash != current_hash:
            return None, current_hash
        return entry.data, current_hash

    def put_data(self, file_path, data, precomputed_hash=None):
        if precomputed_hash is None:
            precomputed_hash = self.compute_hash(file_path)

        self.cache[file_path] = CacheEntry(precomputed_hash, data)
