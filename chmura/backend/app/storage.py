import os


class Storage:
    def __init__(self, root=None):
        self.root = root or os.environ.get("STORAGE_ROOT", "/data/files")

    def _full(self, path):
        return os.path.join(self.root, path)

    def save(self, path, data):
        full = self._full(path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "xb") as f:  # "x" = błąd, jeśli plik już istnieje (N5)
            f.write(data)

    def read(self, path):
        with open(self._full(path), "rb") as f:
            return f.read()

    def exists(self, path):
        return os.path.exists(self._full(path))