import json
import urllib.request
import urllib.error

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5-20251001"
TIMEOUT_SECONDS = 8

SYSTEM_PROMPT_TEMPLATE = """You are classifying UI elements for a screen reader user.

Your task: given metadata about a focused UI element that has no accessible label,
return a JSON object with two fields:
  - "category": the URI (starting with colon) from the allowed list below
  - "label": a short (1-4 word) human-readable label describing what this specific element does

Allowed categories (pick the most specific match):
{allowed_uris}

Rules:
- Output ONLY a single JSON object. No prose, no markdown, no code fences.
- "category" must be copied exactly as written above (including the colon prefix).
- "label" must be lowercase, no punctuation, describe the specific action or content.
- If Name is non-empty, the element has visible text — use CommandButton (not an icon category), and use that text as the label.
- Only use IconButton categories (ActionIconButton, ToggleIconButton) when Name is empty.
- Toggle buttons (mute, play/pause, like, follow) → use ToggleIconButton, not ActionIconButton.
- If you cannot determine a label, use ":Unknown" and label "unlabeled element".
"""

USER_PROMPT_TEMPLATE = """Element metadata:
- Role: {role}
- Name: {name}
- Description: {description}
- Window class: {window_class}
- Window text: {window_text}
- App: {app_name}
- Parent role: {parent_role}
- Parent name: {parent_name}
- Sibling labels: {sibling_names}
- Window title: {window_title}

Classify this element."""


def classify(ctx: dict, allowed_uris: list, api_key: str, descriptions: list = None) -> dict:
    """
    Call Claude. Return {"category": URI, "label": str}.
    Raises ValueError for HTTP errors so caller can handle per error code.
    Raises json.JSONDecodeError or KeyError on malformed responses.
    """
    uri_list = descriptions if descriptions else allowed_uris
    system = SYSTEM_PROMPT_TEMPLATE.format(allowed_uris="\n".join(uri_list))
    user = USER_PROMPT_TEMPLATE.format(
        role=ctx.get("role", ""),
        name=ctx.get("name", ""),
        description=ctx.get("description", ""),
        window_class=ctx.get("window_class", ""),
        window_text=ctx.get("window_text", ""),
        app_name=ctx.get("app_name", ""),
        parent_role=ctx.get("parent_role", ""),
        parent_name=ctx.get("parent_name", ""),
        sibling_names=", ".join(ctx.get("sibling_names", [])),
        window_title=ctx.get("window_title", ""),
    )
    body = json.dumps({
        "model": MODEL,
        "max_tokens": 200,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }).encode("utf-8")
    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise ValueError(f"HTTP {e.code}") from e
    except TimeoutError:
        raise TimeoutError("Request timed out")
    text = payload["content"][0]["text"].strip()
    # Strip markdown code fences if model wraps response despite instructions
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    return json.loads(text)
