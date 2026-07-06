import hashlib


def fingerprint(ctx: dict) -> str:
    """SHA-256 fingerprint stable across sessions.
    Prefers automation_id when available; falls back to structural fields.
    Deliberately excludes window_title and window_text (volatile)."""
    if ctx.get("automation_id"):
        raw = "|".join([
            ctx.get("app_name", ""),
            ctx.get("window_class", ""),
            ctx.get("automation_id", ""),
        ])
    else:
        raw = "|".join([
            ctx.get("app_name", ""),
            ctx.get("window_class", ""),
            ctx.get("role", ""),
            ctx.get("html_class", ""),
            ctx.get("parent_role", ""),
            ctx.get("parent_name", ""),
            str(ctx.get("position_in_parent", "")),
            ctx.get("name", ""),
        ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


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
        ctx.get("name", ""),
        ctx.get("html_class", ""),
        ctx.get("parent_name", ""),
        ctx.get("window_text", "")[:50],
    ])
