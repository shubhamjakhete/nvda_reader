class Cache:
    def __init__(self, max_entries: int = 500):
        self._data = {}
        self._max = max_entries

    def lookup(self, key: str):
        return self._data.get(key)

    def store(self, key: str, value: str) -> None:
        if len(self._data) >= self._max:
            self._data.pop(next(iter(self._data)))
        self._data[key] = value


def make_key(ctx: dict) -> str:
    return "|".join([
        ctx.get("app_name", ""),
        ctx.get("window_class", ""),
        ctx.get("role", ""),
        ctx.get("parent_name", ""),
        ctx.get("window_text", "")[:50],
    ])
