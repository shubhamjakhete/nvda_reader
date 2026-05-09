import os, sys
_VENDOR = os.path.join(os.path.dirname(__file__), "_vendor")
if _VENDOR not in sys.path:
    sys.path.insert(0, _VENDOR)

# NVDA ships a stripped Python that lacks xml.dom. Inject stubs before rdflib loads.
try:
    import xml.dom.minidom
except ImportError:
    import types as _types
    _minidom = _types.ModuleType("xml.dom.minidom")
    for _n in ("Attr", "Comment", "Document", "DocumentFragment", "DocumentType",
               "Element", "Entity", "Node", "Notation", "ProcessingInstruction", "Text"):
        setattr(_minidom, _n, type(_n, (), {}))
    _minidom.parseString = lambda s: _minidom.Document()
    sys.modules["xml.dom.minidom"] = _minidom
    if "xml.dom" not in sys.modules:
        _xml_dom = _types.ModuleType("xml.dom")
        _xml_dom.XML_NAMESPACE = "http://www.w3.org/XML/1998/namespace"
        _xml_dom.minidom = _minidom
        sys.modules["xml.dom"] = _xml_dom
        if "xml" not in sys.modules:
            _xml = _types.ModuleType("xml")
            _xml.dom = _xml_dom
            sys.modules["xml"] = _xml
        else:
            sys.modules["xml"].dom = _xml_dom
    else:
        sys.modules["xml.dom"].minidom = _minidom
    del _types, _minidom, _n

# NVDA modules are only available inside NVDA — guarded for Mac-side unit testing
try:
    import globalPluginHandler
    import api
    import ui
    import scriptHandler
    from logHandler import log
    import gui
    from . import context, classifier, cache, settings
    _NVDA_AVAILABLE = True
except ImportError:
    _NVDA_AVAILABLE = False

from .ontology import Ontology


if _NVDA_AVAILABLE:
    class GlobalPlugin(globalPluginHandler.GlobalPlugin):
        scriptCategory = "Context Labeler"

        def __init__(self):
            super().__init__()
            log.info("contextLabeler loaded")
            self._ontology = Ontology.load_default()
            self._cache = cache.Cache()
            gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(
                settings.ContextLabelerPanel
            )

        def terminate(self):
            gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(
                settings.ContextLabelerPanel
            )

        @scriptHandler.script(
            description="Label the currently focused element using AI + ontology",
            gesture="kb:NVDA+shift+l",
        )
        def script_labelFocused(self, gesture):
            try:
                obj = api.getFocusObject()
                ctx = context.extract(obj)
                key = cache.make_key(ctx)
                cached = self._cache.lookup(key)
                if cached:
                    ui.message(cached)
                    return
                api_key = settings.get_api_key()
                if not api_key:
                    ui.message("Context Labeler: API key not set in settings")
                    return
                allowed_uris = self._ontology.leaf_uris()
                result = classifier.classify(ctx, allowed_uris, api_key)
                if not self._ontology.is_valid_leaf(result["category"]):
                    log.warning(f"Claude returned invalid category: {result['category']}")
                    ui.message("unlabeled element — could not classify")
                    return
                human_category = self._ontology.label_for(result["category"])
                speakable = f"{result['label']} — {human_category}"
                self._cache.store(key, speakable)
                ui.message(speakable)
            except Exception as e:
                log.error("contextLabeler error", exc_info=True)
                ui.message("Context Labeler: error — see NVDA log")
