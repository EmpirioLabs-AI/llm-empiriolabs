"""llm plugin for EmpirioLabs.

EmpirioLabs serves frontier open models through one OpenAI-compatible API at
https://api.empiriolabs.ai/v1 . This plugin registers those models with Simon
Willison's ``llm`` CLI.
"""

import json
import time
from pathlib import Path

import llm
from llm.default_plugins.openai_models import Chat

# AsyncChat was added to llm later; degrade gracefully on older versions.
try:
    from llm.default_plugins.openai_models import AsyncChat

    HAS_ASYNC = True
except ImportError:  # pragma: no cover
    HAS_ASYNC = False

API_BASE = "https://api.empiriolabs.ai/v1"

# Fallback catalog used when the live /v1/models call is unavailable. The
# authoritative list is always GET https://api.empiriolabs.ai/v1/models .
FALLBACK_MODELS = (
    "qwen3-7-plus",
    "qwen3-7-max",
    "deepseek-v4-pro",
    "deepseek-v4-flash",
    "glm-5-1",
    "kimi-k2-7-code",
    "minimax-m3",
)


def fetch_cached_json(url, path, cache_timeout, headers=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        mod_time = path.stat().st_mtime
        if time.time() - mod_time < cache_timeout:
            return json.loads(path.read_text())
    try:
        import httpx

        response = httpx.get(url, headers=headers or {}, follow_redirects=True)
        response.raise_for_status()
        data = response.json()
        path.write_text(json.dumps(data))
        return data
    except Exception:
        # Network failure: serve the stale cache if we have one.
        if path.is_file():
            return json.loads(path.read_text())
        raise


def get_model_ids(key=None, skip_cache=False):
    """Return the EmpirioLabs model slugs, preferring the live catalog."""
    headers = {"Authorization": "Bearer {}".format(key)} if key else None
    try:
        data = fetch_cached_json(
            url="{}/models".format(API_BASE),
            path=llm.user_dir() / "empiriolabs_models.json",
            cache_timeout=0 if skip_cache else 3600,
            headers=headers,
        )
        models = data.get("data", data) if isinstance(data, dict) else data
        ids = [m["id"] for m in models if isinstance(m, dict) and m.get("id")]
        if ids:
            return ids
    except Exception:
        pass
    return list(FALLBACK_MODELS)


class _EmpirioLabsChat:
    needs_key = "empiriolabs"
    key_env_var = "EMPIRIOLABS_API_KEY"

    def __init__(self, model_name):
        super().__init__(
            model_name=model_name,
            model_id="empiriolabs/{}".format(model_name),
            api_base=API_BASE,
        )

    def __str__(self):
        return "EmpirioLabs: {}".format(self.model_id)


class EmpirioLabsChat(_EmpirioLabsChat, Chat):
    pass


if HAS_ASYNC:

    class EmpirioLabsAsyncChat(_EmpirioLabsChat, AsyncChat):
        pass


@llm.hookimpl
def register_models(register):
    key = llm.get_key("", "empiriolabs", "EMPIRIOLABS_API_KEY")
    if not key:
        return
    for model_id in get_model_ids(key=key):
        if HAS_ASYNC:
            register(
                EmpirioLabsChat(model_id),
                EmpirioLabsAsyncChat(model_id),
            )
        else:
            register(EmpirioLabsChat(model_id))
