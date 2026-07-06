import json
import os

try:
    import config as _nvda_config
    _CONFIG_AVAILABLE = True
except ImportError:
    _nvda_config = None
    _CONFIG_AVAILABLE = False

MAX_RECORDS = 5000
_LOCAL_FALLBACK = os.path.join(os.path.dirname(__file__), "contextLabeler-labels.json")


def _default_path() -> str:
    if _CONFIG_AVAILABLE:
        try:
            return os.path.join(_nvda_config.getUserDefaultConfigPath(), "contextLabeler-labels.json")
        except Exception:
            pass
    return _LOCAL_FALLBACK


class LabelStore:
    def __init__(self, path: str = None):
        self._path = path or _default_path()
        self._data = {}
        self.load()

    def load(self) -> None:
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except Exception:
            self._data = {}

    def save(self) -> None:
        tmp = self._path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
            os.replace(tmp, self._path)
        except Exception:
            try:
                os.unlink(tmp)
            except Exception:
                pass

    def lookup(self, fp: str):
        return self._data.get(fp)

    def store(self, fp: str, record: dict) -> None:
        self._evict()
        self._data[fp] = record
        self.save()

    def pin(self, fp: str) -> None:
        if fp in self._data:
            self._data[fp]["pinned"] = True
            self.save()

    def delete(self, fp: str) -> None:
        if fp in self._data:
            del self._data[fp]
            self.save()

    def _evict(self) -> None:
        if len(self._data) < MAX_RECORDS:
            return
        for key in list(self._data.keys()):
            if not self._data[key].get("pinned", False):
                del self._data[key]
                if len(self._data) < MAX_RECORDS:
                    break
