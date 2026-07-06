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
from . import speech, store as label_store


if _NVDA_AVAILABLE:
    class GlobalPlugin(globalPluginHandler.GlobalPlugin):
        scriptCategory = "Context Labeler"

        def __init__(self):
            super().__init__()
            log.info("contextLabeler loaded")
            self._ontology = Ontology.load_default()
            self._cache = cache.Cache()
            self._store = label_store.LabelStore()
            gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(
                settings.ContextLabelerPanel
            )
            self._vscode_ttl = os.path.join(os.path.dirname(__file__), "vscode.ttl")
            self._vscode_loaded = False

        def terminate(self):
            gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(
                settings.ContextLabelerPanel
            )

        def _do_classify(self, ctx: dict, fp: str) -> None:
            """Run the classifier, persist the result, and speak it."""
            from datetime import datetime, timezone
            api_key = settings.get_api_key()
            if not api_key:
                ui.message("Context Labeler: API key not set in settings")
                return
            allowed_uris = self._ontology.leaf_uris()
            descriptions = self._ontology.leaf_descriptions()
            result = classifier.classify(ctx, allowed_uris, api_key, descriptions)
            category = result["category"]
            # Claude returns short form ":Foo" — expand to full URI for validation
            if category.startswith(":"):
                category = "http://contextlabeler.org/ui-ontology#" + category[1:]
            if self._ontology.is_valid_leaf(category):
                tier = speech.TIER_UNVERIFIED if category.endswith("#Unknown") else speech.TIER_VERIFIED
                spoken_class = self._ontology.label_for(category)
            else:
                ancestor = self._ontology.nearest_valid_ancestor(category)
                if ancestor:
                    tier = speech.TIER_PARTIAL
                    spoken_class = self._ontology.label_for(ancestor)
                    log.warning(f"contextLabeler: invalid leaf {category}, fell back to {ancestor}")
                else:
                    tier = speech.TIER_UNVERIFIED
                    spoken_class = ""
            speakable = speech.compose(result["label"], spoken_class, tier)
            rec = {
                "label": result["label"],
                "category": category,
                "tier": tier,
                "pinned": False,
                "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "model": classifier.MODEL,
            }
            self._store.store(fp, rec)
            self._cache.store(fp, speakable)
            ui.message(speakable)

        @scriptHandler.script(
            description="Label the currently focused element using AI + ontology",
            gesture="kb:NVDA+shift+l",
        )
        def script_labelFocused(self, gesture):
            try:
                obj = api.getFocusObject()
                ctx = context.extract(obj)
                if ctx.get("app_name") == "code" and not self._vscode_loaded:
                    self._ontology.load_supplement(self._vscode_ttl)
                    self._vscode_loaded = True
                fp = cache.fingerprint(ctx)
                # Hot in-memory layer
                cached = self._cache.lookup(fp)
                if cached:
                    ui.message(cached)
                    return
                # Persistent store — deterministic replay
                record = self._store.lookup(fp)
                if record:
                    spoken_class = ""
                    try:
                        spoken_class = self._ontology.label_for(record["category"])
                    except Exception:
                        pass
                    speakable = speech.compose(record["label"], spoken_class, record["tier"])
                    self._cache.store(fp, speakable)
                    ui.message(speakable)
                    return
                self._do_classify(ctx, fp)
            except Exception as e:
                log.error("contextLabeler error", exc_info=True)
                ui.message("Context Labeler: error — see NVDA log")

        @scriptHandler.script(
            description="Pin the stored label for the focused element",
            gesture="kb:NVDA+shift+k",
        )
        def script_pinLabel(self, gesture):
            try:
                obj = api.getFocusObject()
                ctx = context.extract(obj)
                fp = cache.fingerprint(ctx)
                if self._store.lookup(fp):
                    self._store.pin(fp)
                    ui.message("label pinned")
                else:
                    ui.message("no label stored for this element")
            except Exception as e:
                log.error("contextLabeler error", exc_info=True)
                ui.message("Context Labeler: error — see NVDA log")

        @scriptHandler.script(
            description="Force re-query the AI label for the focused element",
            gesture="kb:NVDA+shift+r",
        )
        def script_relabelFocused(self, gesture):
            try:
                obj = api.getFocusObject()
                ctx = context.extract(obj)
                fp = cache.fingerprint(ctx)
                record = self._store.lookup(fp)
                if record and record.get("pinned", False):
                    ui.message("label is pinned — unpin to regenerate")
                    return
                self._store.delete(fp)
                self._cache._data.pop(fp, None)
                self._do_classify(ctx, fp)
            except Exception as e:
                log.error("contextLabeler error", exc_info=True)
                ui.message("Context Labeler: error — see NVDA log")
