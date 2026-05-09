def extract(obj) -> dict:
    """
    Extract text-only context from an NVDAObject.
    Returns a dict with these keys (any may be empty string):
      role, name, description, window_class, window_text, app_name,
      parent_name, parent_role, sibling_names, window_title
    Never raises; returns empty strings on any AttributeError.
    """
    def safe(fn):
        try:
            return fn() or ""
        except Exception:
            return ""

    try:
        import controlTypes
        role = safe(lambda: controlTypes.roleLabels.get(obj.role, str(obj.role)))
    except Exception:
        role = safe(lambda: str(obj.role))

    name = safe(lambda: obj.name)
    description = safe(lambda: obj.description)
    window_class = safe(lambda: obj.windowClassName)
    window_text = safe(lambda: obj.windowText)
    app_name = safe(lambda: obj.appModule.appName)

    parent = None
    try:
        parent = obj.parent
    except Exception:
        pass

    parent_name = ""
    parent_role = ""
    if parent is not None:
        parent_name = safe(lambda: parent.name)
        try:
            import controlTypes
            parent_role = safe(lambda: controlTypes.roleLabels.get(parent.role, str(parent.role)))
        except Exception:
            parent_role = safe(lambda: str(parent.role))

    sibling_names = []
    if parent is not None:
        try:
            for child in parent.children:
                if child is obj:
                    continue
                n = ""
                try:
                    n = child.name or ""
                except Exception:
                    pass
                if n:
                    sibling_names.append(n)
                if len(sibling_names) >= 5:
                    break
        except Exception:
            pass

    try:
        import api as nvda_api
        fg = nvda_api.getForegroundObject()
        window_title = safe(lambda: fg.name)
    except Exception:
        window_title = ""

    return {
        "role": role,
        "name": name,
        "description": description,
        "window_class": window_class,
        "window_text": window_text,
        "app_name": app_name,
        "parent_name": parent_name,
        "parent_role": parent_role,
        "sibling_names": sibling_names,
        "window_title": window_title,
    }
